import paho.mqtt.client as mqtt
import time
import os
from picamera2 import Picamera2
from groq import Groq
import requests
from gtts import gTTS
import base64
import json
import speech_recognition as sr
import tempfile
import subprocess

# -------------------------------
# CONFIGURACIÓN MQTT & SISTEMA
# -------------------------------
BROKER_IP = "127.0.0.1"
TOPIC = "robot/distancia"
UMBRAL_DISTANCIA = 45.0

# -------------------------------
# API KEYS
# -------------------------------
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyDSZMkphVRVJenyacVR2USWJl1IzPiGCmY"

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-preview-09-2025:generateContent"
    f"?key={GEMINI_API_KEY}"
)

# -------------------------------
# CLIENTE GROQ
# -------------------------------
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print("❌ Error: No se pudo inicializar Groq:", e)
    groq_client = None

# -------------------------------
# CÁMARA (Picamera2)
# -------------------------------
picam2 = None
try:
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    print("📸 Cámara lista.")
    time.sleep(2)
except Exception as e:
    print(f"❌ Error iniciando cámara: {e}")

# -------------------------------
# UTILIDADES
# -------------------------------
def image_to_base64(filepath):
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def detectar_emocion_con_ia(image_path):
    """Envía la imagen a Gemini y devuelve la emoción (una palabra)."""
    print("🤖 Enviando imagen a Gemini...")
    base64_image = image_to_base64(image_path)
    if not base64_image:
        return "desconocida"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Analiza la emoción principal de la persona. Responde con una sola palabra."},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    }

    try:
        r = requests.post(GEMINI_API_URL, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        emocion = data["candidates"][0]["content"]["parts"][0]["text"]
        return emocion.strip().lower()
    except Exception as e:
        print(f"❌ Error con Gemini: {e}")
        return "desconocida"


def generar_respuesta_groq(emocion, contexto_usuario=None):
    """Genera una respuesta corta y empática desde Groq, dado la emoción y contexto opcional."""
    if not groq_client:
        return "Perdón, ahora no puedo pensar."

    prompt = f"Eres un robot de apoyo emocional. Da una respuesta breve y cálida para alguien que muestra '{emocion}'. Máximo 30 palabras. Español."
    if contexto_usuario:
        prompt += f" Además, la persona dijo: '{contexto_usuario}'. Responde de forma empática."

    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error Groq:", e)
        return "Lo siento, tuve un problema para pensar."


# -------------------------------
# AUDIO: TTS y reproducción confiable con Bluetooth
# -------------------------------
def hablar_mensaje(texto):
    """
    Convierte texto a voz con gTTS y reproduce usando paplay (PipeWire respeta sink Bluetooth).
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            ruta_mp3 = f.name
        tts = gTTS(text=texto, lang='es')
        tts.save(ruta_mp3)

        # Convertir mp3 a wav para paplay
        ruta_wav = ruta_mp3.replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", ruta_mp3, ruta_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Reproducir con paplay
        subprocess.run(["paplay", ruta_wav])

    except Exception as e:
        print("❌ Error al reproducir audio:", e)
    finally:
        for f in [ruta_mp3, ruta_wav]:
            if os.path.exists(f):
                os.remove(f)


# -------------------------------
# AUDIO: Escuchar con SpeechRecognition
# -------------------------------
def escuchar_y_transcribir(timeout=8, phrase_time_limit=8):
    """
    Escucha por el micrófono y devuelve texto.
    Devuelve "" si no entiende o hay error.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone(device_index=2) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("🎤 Escuchando... (habla ahora)")
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("⚠️ Timeout: no se detectó voz.")
                return ""
    except Exception as e:
        print("❌ Error accediendo al micrófono:", e)
        return ""

    try:
        texto = recognizer.recognize_google(audio, language="es-PE")
        print("🗣️ Detectado (STT):", texto)
        return texto
    except sr.UnknownValueError:
        print("⚠️ No entendí (STT).")
        return ""
    except sr.RequestError as e:
        print("❌ Error servicio STT:", e)
        return ""


# -------------------------------
# FLUJO DE INTERACCIÓN
# -------------------------------
def conversacion_continua(inicio_saludo):
    frases_finales = [
        "gracias estoy bien",
        "estoy bien gracias",
        "ya estoy bien",
        "todo bien gracias"
    ]

    hablar_mensaje(inicio_saludo)
    time.sleep(0.4)

    hablar_mensaje("Si quieres, podemos conversar. Dime lo que sientes o di 'gracias estoy bien' para terminar.")
    time.sleep(0.3)

    while True:
        texto_usuario = escuchar_y_transcribir(timeout=8, phrase_time_limit=10)
        if not texto_usuario:
            hablar_mensaje("No te escuché. ¿Quieres intentarlo otra vez? O si deseas terminar, di 'gracias estoy bien'.")
            continue

        normalizado = texto_usuario.strip().lower()

        # 🚨 DETECCIÓN DE FIN DE CONVERSACIÓN Y APAGADO 🚨
        if any(frase in normalizado for frase in frases_finales):
            hablar_mensaje("Me alegra que estés bien. Descansaré por ahora.")
            print("🛑 Apagando robot por frase de cierre...")
            os._exit(0)   # <-- Apaga TODO el robot
            return

        respuesta_ia = generar_respuesta_groq("conversación", contexto_usuario=texto_usuario)
        print("🤖 IA responde:", respuesta_ia)
        hablar_mensaje(respuesta_ia)

# -------------------------------
# DETECCIÓN DE EMOCIÓN
# -------------------------------
def deteccion_emocion(distancia):
    ruta_imagen = "/tmp/rostro_capturado.jpg"
    print(f"\n--- PERSONA DETECTADA A {distancia:.1f} cm ---")

    try:
        if picam2:
            picam2.capture_file(ruta_imagen)
            print("📸 Imagen capturada.")
        else:
            print("⚠️ picam2 no inicializada, no se toma foto.")
    except Exception as e:
        print("❌ Error al capturar imagen:", e)

    emocion = detectar_emocion_con_ia(ruta_imagen)
    print(f"😊 Emoción detectada: {emocion}")

    respuesta = generar_respuesta_groq(emocion)
    print(f"💬 Respuesta creada: {respuesta}")

    hablar_mensaje(respuesta)
    conversacion_continua("Si quieres, podemos hablar ahora mismo.")


# -------------------------------
# MQTT: callbacks
# -------------------------------
def on_message(client, userdata, msg):
    try:
        distancia = float(msg.payload.decode())
        if 0 < distancia < UMBRAL_DISTANCIA:
            print(f"🚨 Persona cerca: {distancia} cm")
            deteccion_emocion(distancia)
        else:
            print(f"Distancia: {distancia} cm")
    except Exception as e:
        print("⚠️ Mensaje inválido:", e)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📡 Conectado a MQTT")
        client.subscribe(TOPIC)
    else:
        print("❌ Error MQTT, rc=", rc)


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    try:
        client = mqtt.Client(client_id="Pi5_Robot_Ansiedad", protocol=mqtt.MQTTv311)
        client.on_connect = on_connect
        client.on_message = on_message

        print("🔌 Conectando al broker MQTT...")
        client.connect(BROKER_IP, 1883, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n🛑 Programa detenido por el usuario (Ctrl+C).")
    except Exception as e:
        print("❌ Error crítico:", e)


