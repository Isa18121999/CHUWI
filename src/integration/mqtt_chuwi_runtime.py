class MQTTChuwiRuntime:
    """Adapta mensajes MQTT de distancia al runtime de Chuwi."""

    def __init__(self, chuwi_runtime):
        self.chuwi_runtime = chuwi_runtime

    def on_message(self, topic, payload):
        try:
            distance = float(payload.decode())
            self.handle_distance(distance)
        except (UnicodeDecodeError, TypeError, ValueError) as error:
            print("MQTT Chuwi error:", error)

    def handle_distance(self, distance):
        if distance <= 80:
            self.chuwi_runtime.activate_interaction()
        else:
            self.chuwi_runtime.return_idle()
