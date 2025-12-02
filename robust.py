from .simple import MQTTClient, MQTTException
import utime

class MQTTClient(MQTTClient):
    def reconnect(self):
        try:
            self.disconnect()
        except:
            pass
        utime.sleep(1)
        self.connect()

    def publish(self, topic, msg, retain=False, qos=0):
        try:
            super().publish(topic, msg, retain, qos)
        except Exception as e:
            print("⚠️ MQTT publish failed:", e)
            self.reconnect()
            super().publish(topic, msg, retain, qos)

    def check_msg(self):
        try:
            return super().check_msg()
        except OSError as e:
            print("⚠️ MQTT check_msg error:", e)
            self.reconnect()