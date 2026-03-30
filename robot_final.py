import cv2  
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
  
from groq import Groq  
  
# -------------------------------  
# API KEYS (REEMPLAZAR CON TUS CLAVES)  
# -------------------------------  
GROQ_API_KEY = ""  # Agrega tu clave API de GROQ aquí  
GEMINI_API_KEY = ""  # Agrega tu clave API de GEMINI aquí  
ELEVENLABS_API_KEY = ""  # Agrega tu clave API de ELEVENLABS aquí  
ELEVENLABS_VOICE_ID = ""  # Agrega tu ID de voz de ElevenLabs aquí  
  
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
        subprocess.run(["mpg123", "-a", "alsa", ruta])  
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
  
            subprocess.run(["aplay", wav])  
  
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
    cap.release()  
    sys.exit(0)  
  
signal.signal(signal.SIGINT, salir)  
  
# -------------------------------  
# CÁMARA USB  
# -------------------------------  
cap = cv2.VideoCapture(0)  
  
if not cap.isOpened():  
    print("❌ No se pudo abrir la cámara")  
    exit()  
  
print("✅ Cámara lista")  
  
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
        with sr.Microphone() as source:  
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
    ret, frame = cap.read()  
  
    if not ret:  
        return False  
  
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
  
    return len(faces) > 0  
  
# -------------------------------  
# FOTO  
# -------------------------------  
def tomar_foto(ruta):  
    ret, frame = cap.read()  
    if ret:  
        cv2.imwrite(ruta, frame)  
  
# -------------------------------  
# FLUJO PRINCIPAL  
# -------------------------------  
def activar_robot():  
    print("🚨 Persona detectada")  
  
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
  
# -------------------------------  
# LOOP  
# -------------------------------  
print("👀 Esperando persona...")  
  
while True:  
    try:  
        if detectar_persona():  
            activar_robot()  
            time.sleep(5)  
  
        time.sleep(0.3)  
  
    except KeyboardInterrupt:  
        print("🛑 detenido")  
        break  
  
cap.release()