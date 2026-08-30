import json


class MQTTChuwiRuntime:
    """Connects distance MQTT messages with Chuwi runtime."""

    def __init__(self, chuwi_runtime):
        self.chuwi_runtime = chuwi_runtime

    def on_message(self, topic, payload):
        try:
            distance = float(payload.decode())
            self.chuwi_runtime.process_distance(distance)
        except Exception as error:
            print("MQTT Chuwi error:", error)

    def handle_distance(self, distance):
        if distance <= 80:
            self.chuwi_runtime.activate_interaction()
        else:
            self.chuwi_runtime.return_idle()
