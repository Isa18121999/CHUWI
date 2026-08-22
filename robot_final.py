pi@raspberrypi:~ $ cd robot_env
pi@raspberrypi:~/robot_env $ cat robot_final.py
import cv2
import threading
import time
import os
import base64
import requests
import speech_recognition as sr
import subprocess
import tempfile
import signal
import sys
import asyncio
import edge_tts
import re

robot_ocupado = False
SALUDO_INICIAL = "Hola, me llamo Chuwi. Â¿CÃ³mo te llamas?"

from groq import Groq
from picamera2 import Picamera2
# -------------------------------
# API KEYS
# -------------------------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

groq_client = Groq(api_key=GROQ_API_KEY)

# -------------------------------
# VOZ EDGE TTS (FEMENINA)
# -------------------------------
async def hablar_edge(texto):
    try:
        communicate = edge_tts.Communicate(
            text=f"{texto}...",
            voice="es-MX-DaliaNeural"
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            ruta = f.name

        await communicate.save(ruta)
        subprocess.run(["paplay", ruta])
        os.remove(ruta)

    except Exception as e:
        print("âŒ Error Edge TTS:", e)

# -------------------------------
# VOZ PRINCIPAL
# -------------------------------
def hablar(texto):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }

        data = {
            "text": texto,
            "model_id": "eleven_monolingual_v1"
        }

        r = requests.post(url, json=data, headers=headers)

        if r.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(r.content)
                ruta = f.name

            wav = ruta.replace(".mp3", ".wav")

            subprocess.run(
                ["ffmpeg", "-y", "-i", ruta, wav],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            subprocess.run(["paplay", wav])

            os.remove(ruta)
            os.remove(wav)
        else:
            raise Exception("ElevenLabs fallÃ³")

    except:
        print("âš ï¸ ElevenLabs fallÃ³, usando Edge TTS")
        asyncio.run(hablar_edge(texto))

# -------------------------------
# SALIDA LIMPIA
# -------------------------------
def salir(sig, frame):
    print("\nðŸ›‘ Robot detenido")
    picam2.stop()
    sys.exit(0)


# -------------------------------
# CÃMARA USB
# -------------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

print("âœ… CÃ¡mara lista (Picamera2)")


# -------------------------------
# DETECTOR ROSTRO
# -------------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -------------------------------
# ESCUCHAR (MIC DE LA CÃMARA)
# -------------------------------
def escuchar():
    r = sr.Recognizer()

    try:
        with sr.Microphone(device_index=0) as source:
            print("ðŸŽ¤ Escuchando...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=6)

        texto = r.recognize_google(audio, language="es-PE")
        print("ðŸ—£ï¸ TÃº:", texto)
        return texto

    except Exception as e:
        print("âŒ Error mic:", e)
        return ""


def extraer_nombre(texto):
    coincidencia = re.search(
        r"(?:me llamo|mi nombre es|soy)\s+([A-Za-zÃÃ‰ÃÃ“ÃšÃœÃ‘Ã¡Ã©Ã­Ã³ÃºÃ¼Ã±]{2,30})",
        texto,
        flags=re.IGNORECASE,
    )
    if coincidencia:
        return coincidencia.group(1).capitalize()
    palabras = texto.strip().split()
    if len(palabras) == 1 and palabras[0].isalpha() and len(palabras[0]) <= 30:
        return palabras[0].capitalize()
    return None

# -------------------------------
# GEMINI (EMOCIÃ“N)
# -------------------------------
def image_to_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def detectar_emocion(image_path):
    try:
        base64_image = image_to_base64(image_path)

        payload = {
            "contents": [{
                "parts": [
                    {"text": "Dime la emociÃ³n en una palabra"},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }]
        }

        r = requests.post(GEMINI_API_URL, json=payload)
        data = r.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except:
        return "neutral"

# -------------------------------
# IA CON MEMORIA
# -------------------------------
historial = []

def generar_respuesta(emocion, texto=None):
    global historial

    if texto:
        historial.append(f"Usuario: {texto}")

    contexto = "\n".join(historial[-6:])

    prompt = f"""
Eres Chuwibot, un robot emocional para niÃ±os hospitalizados.

Responde de forma:
- corta
- cÃ¡lida
- amigable
- natural

Contexto:
{contexto}

EmociÃ³n detectada: {emocion}
"""

    res = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"
    )

    respuesta = res.choices[0].message.content

    historial.append(f"Chuwi: {respuesta}")

    return respuesta

# -------------------------------
# DETECTAR PERSONA
# -------------------------------
def detectar_persona():
    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return len(faces) > 0
# -------------------------------
# FOTO
# -------------------------------
def tomar_foto(ruta):
    frame = picam2.capture_array()
    cv2.imwrite(ruta, frame)
# -------------------------------
# FLUJO PRINCIPAL
# -------------------------------
def activar_robot():
    global robot_ocupado

    if robot_ocupado:
        return

    robot_ocupado = True

    def run():
        global robot_ocupado

        print("ðŸš¨ Persona detectada")

        # El saludo no debe depender de la detecciÃ³n emocional ni de una API.
        hablar(SALUDO_INICIAL)
        respuesta_nombre = escuchar()
        nombre = extraer_nombre(respuesta_nombre) if respuesta_nombre else None
        hablar(
            f"Mucho gusto, {nombre}. Voy a acompaÃ±arte un momento."
            if nombre else "Mucho gusto. Voy a acompaÃ±arte un momento."
        )

        ruta = "/tmp/foto.jpg"
        tomar_foto(ruta)

        emocion = detectar_emocion(ruta)
        print("ðŸ˜Š:", emocion)

        hablar(generar_respuesta(emocion))

        intentos = 0

        while True:
            texto = escuchar()

            if not texto:
                intentos += 1
                if intentos >= 3:
                    hablar("No te escuchÃ© bien, volverÃ© a esperar")
                    break
                continue

            if "gracias" in texto.lower():
                hablar("Fue lindo hablar contigo")
                break

            respuesta = generar_respuesta("conversaciÃ³n", texto)
            hablar(respuesta)

        robot_ocupado = False

    threading.Thread(target=run).start()
# -------------------------------
# LOOP
# -------------------------------
print("ðŸ‘€ Esperando persona...")

while True:
    try:
        if detectar_persona():
            activar_robot()

        time.sleep(0.3)

    except KeyboardInterrupt:
        break

cap.release()
async def hablar_edge(texto):
    try:
        communicate = edge_tts.Communicate(
            text=f"{texto}...",
            voice="es-MX-DaliaNeural"
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            ruta = f.name

        await communicate.save(ruta)
        subprocess.run(["paplay", ruta])
        os.remove(ruta)

    except Exception as e:
        print("❌ Error Edge TTS:", e)

# -------------------------------
# VOZ PRINCIPAL
# -------------------------------
def hablar(texto):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }

        data = {
            "text": texto,
            "model_id": "eleven_monolingual_v1"
        }

        r = requests.post(url, json=data, headers=headers)

        if r.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(r.content)
                ruta = f.name

            wav = ruta.replace(".mp3", ".wav")

            subprocess.run(
                ["ffmpeg", "-y", "-i", ruta, wav],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            subprocess.run(["paplay", wav])

            os.remove(ruta)
            os.remove(wav)
        else:
            raise Exception("ElevenLabs falló")

    except:
        print("⚠️ ElevenLabs falló, usando Edge TTS")
        asyncio.run(hablar_edge(texto))

# -------------------------------
# SALIDA LIMPIA
# -------------------------------
def salir(sig, frame):
    print("\n🛑 Robot detenido")
    picam2.stop()
    sys.exit(0)


# -------------------------------
# CÁMARA USB
# -------------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

print("✅ Cámara lista (Picamera2)")


# -------------------------------
# DETECTOR ROSTRO
# -------------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -------------------------------
# ESCUCHAR (MIC DE LA CÁMARA)
# -------------------------------
def escuchar():
    r = sr.Recognizer()

    try:
        with sr.Microphone(device_index=0) as source:
            print("🎤 Escuchando...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=6)

        texto = r.recognize_google(audio, language="es-PE")
        print("🗣️ Tú:", texto)
        return texto

    except Exception as e:
        print("❌ Error mic:", e)
        return ""

# -------------------------------
# GEMINI (EMOCIÓN)
# -------------------------------
def image_to_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def detectar_emocion(image_path):
    try:
        base64_image = image_to_base64(image_path)

        payload = {
            "contents": [{
                "parts": [
                    {"text": "Dime la emoción en una palabra"},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }]
        }

        r = requests.post(GEMINI_API_URL, json=payload)
        data = r.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except:
        return "neutral"

# -------------------------------
# IA CON MEMORIA
# -------------------------------
historial = []

def generar_respuesta(emocion, texto=None):
    global historial

    if texto:
        historial.append(f"Usuario: {texto}")

    contexto = "\n".join(historial[-6:])

    prompt = f"""
Eres Chuwibot, un robot emocional para niños hospitalizados.

Responde de forma:
- corta
- cálida
- amigable
- natural

Contexto:
{contexto}

Emoción detectada: {emocion}
"""

    res = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"
    )

    respuesta = res.choices[0].message.content

    historial.append(f"Chuwi: {respuesta}")

    return respuesta

# -------------------------------
# DETECTAR PERSONA
# -------------------------------
def detectar_persona():
    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return len(faces) > 0
# -------------------------------
# FOTO
# -------------------------------
def tomar_foto(ruta):
    frame = picam2.capture_array()
    cv2.imwrite(ruta, frame)
# -------------------------------
# FLUJO PRINCIPAL
# -------------------------------
def activar_robot():
    global robot_ocupado

    if robot_ocupado:
        return

    robot_ocupado = True

    def run():
        global robot_ocupado

        print("🚨 Persona detectada")
     # El saludo no debe depender de la detección emocional ni de una API.
        hablar(SALUDO_INICIAL)
        ruta = "/tmp/foto.jpg"
        tomar_foto(ruta)

        emocion = detectar_emocion(ruta)
        print("😊:", emocion)

        hablar(generar_respuesta(emocion))

        intentos = 0

        while True:
            texto = escuchar()

            if not texto:
                intentos += 1
                if intentos >= 3:
                    hablar("No te escuché bien, volveré a esperar")
                    break
                continue

            if "gracias" in texto.lower():
                hablar("Fue lindo hablar contigo")
                break

            respuesta = generar_respuesta("conversación", texto)
            hablar(respuesta)

        robot_ocupado = False

    threading.Thread(target=run).start()
# -------------------------------
# LOOP
# -------------------------------
print("👀 Esperando persona...")

while True:
    try:
        if detectar_persona():
            activar_robot()

        time.sleep(0.3)

    except KeyboardInterrupt:
        break

cap.release()
