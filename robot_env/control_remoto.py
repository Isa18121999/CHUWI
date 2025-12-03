import paho.mqtt.client as mqtt
import time

BROKER_IP = "172.20.10.2"  # Ejemplo: "192.168.1.50"
TOPIC = "robot/iniciar"

client = mqtt.Client()

print("📡 Conectando al broker...")
client.connect(BROKER_IP, 1883, 60)

print("▶ Enviando señal de inicio...")
client.publish(TOPIC, "start")

print("✔ Señal enviada. Robot activándose.")
time.sleep(1)

