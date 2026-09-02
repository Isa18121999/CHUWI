class ChuwiMQTTBridge:
    """Adapta mensajes MQTT de distancia al controlador y al rostro de Chuwi."""

    def __init__(self, controller, face, distance_limit=80):
        self.controller = controller
        self.face = face
        self.distance_limit = distance_limit

    def on_distance_message(self, payload):
        try:
            distance = float(payload)
        except (TypeError, ValueError):
            return None

        if distance <= self.distance_limit:
            self.controller.change_state("DETECTED")
            self.face.change_expression("WELCOME")
            return "DETECTED"

        self.controller.change_state("IDLE")
        self.face.change_expression("IDLE")
        return "IDLE"

    def handle_message(self, topic, message):
        if isinstance(message, bytes):
            message = message.decode("utf-8", errors="replace")
        return self.on_distance_message(message)
