import asyncio
import base64
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time

import cv2
import edge_tts
import requests
import speech_recognition as sr
from groq import Groq
from picamera2 import Picamera2

robot_ocupado = False
ultima_distancia_cm = None
DISTANCIA_ACTIVACION_CM = float(os.environ.get("CHUWI_DISTANCIA_ACTIVACION_CM", "80"))
MQTT_BROKER_IP = os.environ.get("MQTT_BROKER_IP", "172.20.10.2")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "robot/distancia")

SALUDO_INICIAL = "Hola, me llamo Chuwi. ¿Cómo te llamas?"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

if not GROQ_API_KEY:
    raise RuntimeError("Falta GROQ_API_KEY en las variables de entorno")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY no configurada; emoción = neutral")

if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
    print("⚠️ ElevenLabs no configurado; se usará Edge TTS")

groq_client = Groq(api_key=GROQ_API_KEY)


def reproducir_mp3(ruta_mp3):
    wav = ruta_mp3.replace(".mp3", ".wav")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ruta_mp3, wav],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(["paplay", wav], check=False)
    finally:
        for ruta in (ruta_mp3, wav):
            try:
                os.remove(ruta)
            except FileNotFoundError:
                pass


async def hablar_edge(texto):
    ruta = None
    try:
        communicate = edge_tts.Communicate(
            text=f"{texto}...",
            voice="es-MX-DaliaNeural",
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            ruta = f.name

        await communicate.save(ruta)
        subprocess.run(["paplay", ruta], check=False)
    except Exception as e:
        print("❌ Error Edge TTS:", e)
    finally:
        if ruta:
            try:
                os.remove(ruta)
            except FileNotFoundError:
                pass


def hablar(texto):
    try:
        if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
            raise RuntimeError("ElevenLabs no configurado")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        data = {
            "text": texto,
            "model_id": "eleven_monolingual_v1",
        }

        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(response.content)
            ruta = f.name

        reproducir_mp3(ruta)

    except Exception as e:
        print("⚠️ ElevenLabs falló:", e)
        asyncio.run(hablar_edge(texto))


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

print("✅ Cámara lista (Picamera2)")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

if face_cascade.empty():
    raise RuntimeError("No se pudo cargar el clasificador Haar de rostro")


def escuchar():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone(device_index=0) as source:
            print("🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

        texto = recognizer.recognize_google(audio, language="es-PE")
        print("🗣️ Tú:", texto)
        return texto.strip()

    except sr.WaitTimeoutError:
        print("⏱️ No hubo respuesta")
    except sr.UnknownValueError:
        print("❓ No se entendió el audio")
    except sr.RequestError as e:
        print("❌ Error del servicio de reconocimiento:", e)
    except Exception as e:
        print("❌ Error mic:", e)

    return ""


def extraer_nombre(texto):
    texto = texto.strip()
    if not texto:
        return None

    coincidencia = re.search(
        r"(?:me llamo|mi nombre es|soy)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,30})",
        texto,
        flags=re.IGNORECASE,
    )
    if coincidencia:
        return coincidencia.group(1).capitalize()

    palabras = texto.split()
    if len(palabras) == 1 and palabras[0].isalpha() and len(palabras[0]) <= 30:
        return palabras[0].capitalize()

    return None


def image_to_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def detectar_emocion(image_path):
    if not GEMINI_API_KEY:
        return "neutral"

    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Analiza únicamente la expresión facial visible. "
                                "Responde con una sola palabra en español de esta lista: "
                                "feliz, triste, enojado, asustado, sorprendido, neutral."
                            )
                        },
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": image_to_base64(image_path),
                            }
                        },
                    ]
                }
            ]
        }

        response = requests.post(GEMINI_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        emocion = data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()

        emociones_validas = {
            "feliz",
            "triste",
            "enojado",
            "asustado",
            "sorprendido",
            "neutral",
        }
        return emocion if emocion in emociones_validas else "neutral"

    except Exception as e:
        print("❌ Error Gemini:", e)
        return "neutral"


historial = []


def generar_respuesta(emocion, texto=None):
    global historial

    if texto:
        historial.append(f"Usuario: {texto}")

    contexto = "\n".join(historial[-6:])

    prompt = f"""
Eres Chuwi, un robot social de apoyo emocional para niños hospitalizados.

Responde en español y de manera:
- corta
- cálida
- amigable
- natural
- apropiada para un niño

No reemplazas a médicos, psicólogos ni familiares.
No diagnostiques ni afirmes que conoces con certeza el estado emocional del niño.
No uses respuestas alarmantes.

Contexto de la conversación:
{contexto}

Emoción observada por visión computacional: {emocion}

Genera una respuesta breve para continuar la conversación.
"""

    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=100,
        )
        respuesta = response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error Groq:", e)
        respuesta = "Estoy aquí contigo. ¿Quieres contarme cómo te sientes?"

    historial.append(f"Chuwi: {respuesta}")
    return respuesta


def detectar_persona():
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    return len(faces) > 0


def tomar_foto(ruta):
    frame = picam2.capture_array()
    cv2.imwrite(ruta, frame)


def manejar_distancia(mensaje):
    global ultima_distancia_cm

    try:
        distancia = float(mensaje.decode() if isinstance(mensaje, bytes) else mensaje)
    except (TypeError, ValueError):
        print("⚠️ Distancia MQTT inválida:", mensaje)
        return

    ultima_distancia_cm = distancia
    print(f"📏 Distancia MQTT: {distancia:.2f} cm")

    if distancia <= DISTANCIA_ACTIVACION_CM:
        activar_robot()


def escuchar_mqtt():
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("⚠️ paho-mqtt no instalado; se usará solo detección por cámara")
        return None

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print(f"✅ MQTT conectado a {MQTT_BROKER_IP}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Suscrito a {MQTT_TOPIC}")
        else:
            print("❌ Error de conexión MQTT:", reason_code)

    def on_message(client, userdata, message):
        manejar_distancia(message.payload)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="chuwi_pi5")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER_IP, MQTT_PORT, keepalive=30)
        client.loop_start()
        return client
    except Exception as e:
        print("⚠️ No se pudo conectar al broker MQTT:", e)
        return None


def activar_robot():
    global robot_ocupado, historial

    if robot_ocupado:
        return

    robot_ocupado = True
    historial = []

    def run():
        global robot_ocupado

        try:
            print("🚨 Activando interacción con Chuwi")

            hablar(SALUDO_INICIAL)

            respuesta_nombre = escuchar()
            nombre = extraer_nombre(respuesta_nombre)

            if nombre:
                hablar(f"Mucho gusto, {nombre}. Voy a acompañarte un momento.")
            else:
                hablar("Mucho gusto. Voy a acompañarte un momento.")

            ruta = "/tmp/chuwi_foto.jpg"
            tomar_foto(ruta)

            emocion = detectar_emocion(ruta)
            print("😊 Emoción observada:", emocion)

            hablar(generar_respuesta(emocion))

            intentos = 0
            while True:
                texto = escuchar()

                if not texto:
                    intentos += 1
                    if intentos >= 3:
                        hablar("No te escuché bien. Volveré a esperarte.")
                        break
                    continue

                intentos = 0
                texto_lower = texto.lower()

                if any(frase in texto_lower for frase in ("gracias", "adiós", "adios", "chau")):
                    hablar("Fue lindo hablar contigo. Nos vemos pronto.")
                    break

                respuesta = generar_respuesta("conversación", texto)
                hablar(respuesta)

        except Exception as e:
            print("❌ Error en la interacción:", e)
        finally:
            robot_ocupado = False

    threading.Thread(target=run, daemon=True).start()


def salir(sig=None, frame=None):
    print("\n🛑 Robot detenido")
    try:
        picam2.stop()
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGINT, salir)
signal.signal(signal.SIGTERM, salir)

mqtt_client = escuchar_mqtt()

print(
    f"👀 Esperando persona... "
    f"(activación MQTT <= {DISTANCIA_ACTIVACION_CM:.0f} cm; cámara como respaldo)"
)

try:
    while True:
        if not mqtt_client and detectar_persona():
            activar_robot()
        time.sleep(0.3)
except KeyboardInterrupt:
    salir()
