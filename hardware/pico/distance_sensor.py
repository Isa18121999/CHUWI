import network
import time
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
BROKER_IP = "YOUR_MQTT_BROKER_IP"
TOPIC = b"robot/distancia"

TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.3)
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
    return round((duracion * 0.0343) / 2, 2)


def conectar_mqtt():
    try:
        client = MQTTClient("picoW_robot", BROKER_IP, port=1883, keepalive=30)
        client.connect()
        return client
    except Exception as error:
        print("MQTT error:", error)
        return None


conectar_wifi()
cliente = conectar_mqtt()

while True:
    if cliente is None:
        time.sleep(1)
        cliente = conectar_mqtt()
        continue

    distancia = medir_distancia()
    mensaje = b"error" if distancia is None else str(distancia).encode()

    try:
        cliente.publish(TOPIC, mensaje)
    except Exception as error:
        print("Publish error:", error)
        try:
            cliente.disconnect()
        except Exception:
            pass
        cliente = None

    time.sleep(2)
