class MQTTChuwiRuntime:
    """Adapta mensajes MQTT de distancia al runtime de Chuwi."""

    def __init__(self, chuwi_runtime):
        self.chuwi_runtime = chuwi_runtime

    def on_message(self, topic, payload):
        try:
            distance = float(payload.decode())
            return self.handle_distance(distance)
        except (UnicodeDecodeError, TypeError, ValueError) as error:
            print("MQTT Chuwi error:", error)
            return None

    def handle_distance(self, distance):
        return self.chuwi_runtime.update(distance)
