import asyncio
import base64
import tempfile
from datetime import datetime, timezone
from enum import Enum

import cv2
import edge_tts
import httpx
import speech_recognition as sr
import subprocess
import os

from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models import Interaccion, SesionRobot
from app.notifications import crear_notificacion
from app.websocket_manager import ws_manager


class RobotState(str, Enum):
    STOPPED = "stopped"
    WAITING = "waiting"
    INTERACTING = "interacting"


class RobotController:
    def __init__(self):
        self.state = RobotState.STOPPED
        self.current_session_id: int | None = None
        self.historial: list[str] = []
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self.cap = None

    @property
    def is_running(self) -> bool:
        return self.state != RobotState.STOPPED

    async def start(self):
        if self.is_running:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        self._stop_event.set()
        if self._task:
            self._task.cancel()
            self._task = None
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.state = RobotState.STOPPED
        await ws_manager.broadcast("robot_state", {"state": self.state.value})

    # --- Camera ---
    def _init_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

    def _detect_face(self) -> bool:
        self._init_camera()
        ret, frame = self.cap.read()
        if not ret:
            return False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces) > 0

    def _take_photo(self, path: str):
        self._init_camera()
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite(path, frame)

    # --- Emotion detection (Gemini) ---
    async def _detect_emotion(self, image_path: str) -> str:
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()

            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.5-flash-preview-09-2025:generateContent?key={settings.GEMINI_API_KEY}"
            )
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Dime la emoción en una palabra"},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b64}},
                    ]
                }]
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, timeout=15)
                data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "neutral"

    # --- AI response (Groq) ---
    async def _generate_response(self, emotion: str, text: str | None = None) -> str:
        if text:
            self.historial.append(f"Usuario: {text}")

        context = "\n".join(self.historial[-6:])
        prompt = (
            "Eres Chuwibot, un robot emocional para niños hospitalizados.\n"
            "Responde de forma: corta, cálida, amigable, natural.\n\n"
            f"Contexto:\n{context}\n\nEmoción detectada: {emotion}"
        )

        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        res = await asyncio.to_thread(
            groq_client.chat.completions.create,
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        response = res.choices[0].message.content
        self.historial.append(f"Chuwi: {response}")
        return response

    # --- TTS ---
    async def _speak(self, text: str, db: AsyncSession):
        # Notification on every speak
        await crear_notificacion(
            db,
            tipo="hablar",
            mensaje=f"Chuwibot dice: {text[:100]}",
            sesion_id=self.current_session_id,
        )
        await ws_manager.broadcast("robot_speak", {
            "text": text,
            "sesion_id": self.current_session_id,
        })

        try:
            communicate = edge_tts.Communicate(text=f"{text}...", voice="es-MX-DaliaNeural")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                path = f.name
            await communicate.save(path)
            await asyncio.to_thread(subprocess.run, ["mpg123", "-a", "alsa", path])
            os.remove(path)
        except Exception as e:
            print(f"TTS error: {e}")

    # --- Listen ---
    async def _listen(self) -> str:
        def _do_listen():
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                    audio = r.listen(source, timeout=5, phrase_time_limit=6)
                return r.recognize_google(audio, language="es-PE")
            except Exception:
                return ""
        return await asyncio.to_thread(_do_listen)

    # --- Save interaction to DB ---
    async def _save_interaction(self, db: AsyncSession, rol: str, texto: str, emocion: str | None = None):
        interaction = Interaccion(
            sesion_id=self.current_session_id,
            rol=rol,
            texto=texto,
            emocion=emocion,
        )
        db.add(interaction)
        await db.commit()

    # --- Main loop ---
    async def _run_loop(self):
        self.state = RobotState.WAITING
        await ws_manager.broadcast("robot_state", {"state": self.state.value})

        while not self._stop_event.is_set():
            try:
                has_face = await asyncio.to_thread(self._detect_face)

                if has_face:
                    await self._interact()

                await asyncio.sleep(0.3)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Robot loop error: {e}")
                await asyncio.sleep(1)

        self.state = RobotState.STOPPED

    async def _interact(self):
        self.state = RobotState.INTERACTING
        await ws_manager.broadcast("robot_state", {"state": self.state.value})

        async with async_session() as db:
            # Create session
            session = SesionRobot()
            db.add(session)
            await db.commit()
            await db.refresh(session)
            self.current_session_id = session.id

            await crear_notificacion(
                db, tipo="activacion",
                mensaje="Persona detectada - interacción iniciada",
                sesion_id=session.id,
            )

            # Take photo and detect emotion
            photo_path = tempfile.mktemp(suffix=".jpg")
            await asyncio.to_thread(self._take_photo, photo_path)
            emotion = await self._detect_emotion(photo_path)

            session.emocion_inicial = emotion
            await db.commit()

            # Generate and speak initial response
            response = await self._generate_response(emotion)
            await self._save_interaction(db, "robot", response, emotion)
            await self._speak(response, db)

            # Conversation loop
            retries = 0
            while not self._stop_event.is_set():
                text = await self._listen()

                if not text:
                    retries += 1
                    if retries >= 3:
                        farewell = "No te escuché bien, volveré a esperar"
                        await self._save_interaction(db, "robot", farewell)
                        await self._speak(farewell, db)
                        break
                    continue

                retries = 0
                await self._save_interaction(db, "usuario", text)

                if "chau" in text.lower():
                    goodbye = "Fue lindo hablar contigo"
                    await self._save_interaction(db, "robot", goodbye)
                    await self._speak(goodbye, db)
                    break

                response = await self._generate_response("conversación", text)
                await self._save_interaction(db, "robot", response)
                await self._speak(response, db)

            # Close session
            session.fin = datetime.now(timezone.utc)
            await db.commit()

        self.current_session_id = None
        self.state = RobotState.WAITING
        await ws_manager.broadcast("robot_state", {"state": self.state.value})
        await asyncio.sleep(5)


robot = RobotController()
