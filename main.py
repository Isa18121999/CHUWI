import network
import time
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

# ---------------- CONFIGURACIÓN ----------------
WIFI_SSID = "HUAWEI nova Y73"
WIFI_PASS = "c72f6226c622"
BROKER_IP = "172.20.10.2"  # IP del Raspberry Pi 5
TOPIC = b"robot/distancia"

TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("✅ WiFi ya conectado:", wlan.ifconfig())
        return wlan

    print("📡 Conectando WiFi...")
    wlan.connect(WIFI_SSID, WIFI_PASS)

    while not wlan.isconnected():
        time.sleep(0.3)

    print("✅ WiFi conectado:", wlan.ifconfig())
    return wlan


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


def conectar_mqtt():
    try:
        cliente = MQTTClient(
            client_id="picoW_robot",
            server=BROKER_IP,
            port=1883,
            keepalive=30,
        )
        cliente.connect()
        print("✅ Conectado al broker MQTT")
        return cliente
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None


# ---------------- INICIO ----------------
conectar_wifi()
cliente = conectar_mqtt()


# ---------------- BUCLE PRINCIPAL ----------------
while True:
    try:
        if cliente is None:
            print("♻️ Reintentando conexión MQTT...")
            time.sleep(1)
            cliente = conectar_mqtt()
            continue

        distancia = medir_distancia()
        mensaje = b"error" if distancia is None else str(distancia).encode()

        try:
            cliente.publish(TOPIC, mensaje)
            print("📏 Enviado:", mensaje)
        except Exception as e:
            print("⚠️ Error publicando MQTT:", e)
            try:
                cliente.disconnect()
            except Exception:
                pass
            cliente = None

        time.sleep(2)

    except Exception as e:
        print("⚠️ Error general:", e)
        cliente = None
        time.sleep(2)
