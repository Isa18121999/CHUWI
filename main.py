# robot_ansiedad_picoW.p
import network
import time
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient
#source robot_env/bin/activate
#python robot_ansiedad_pi5.py

# -------- CONFIGURACIÓN --------
WIFI_SSID = "iPhone de JairML"
WIFI_PASS = "JairML30"
BROKER_IP = "172.20.10.2"   # IP del Pi 5
TOPIC = b"robot/distancia"

TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

# -------- FUNCIONES WIFI --------
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.3)

    print("WiFi OK:", wlan.ifconfig())
    return wlan

# -------- SENSOR ULTRASÓNICO --------
def medir_distancia():
    TRIG.value(0)
    time.sleep_us(5)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    duracion = time_pulse_us(ECHO, 1, 30000)
    if duracion <= 0:
        return None

    distancia = (duracion * 0.0343) / 2
    return round(distancia, 2)

# -------- MQTT --------
def conectar_mqtt():
    try:
        cliente = MQTTClient(
            client_id="picoW_robot",
            server=BROKER_IP,
            port=1883,
            keepalive=30
        )
        cliente.connect()
        print("✅ Conectado al broker MQTT!")
        return cliente
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

# -------- MAIN LOOP --------
conectar_wifi()
cliente = conectar_mqtt()

while True:
    try:
        if cliente is None:
            print("♻️ Reintentando MQTT...")
            cliente = conectar_mqtt()
            time.sleep(1)
            continue

        dist = medir_distancia()
        msg = b"error" if dist is None else str(round(dist, 2)).encode()

        try:
            cliente.publish(TOPIC, msg)
            print("Enviado:", msg)
        except Exception as e:
            print("⚠️ Error publicando:", e)
            cliente = None

        time.sleep(2)

    except Exception as e:
        print("⚠️ Error general:", e)
        time.sleep(2)