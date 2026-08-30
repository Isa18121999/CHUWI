import json

DISTANCE_LIMIT = 80


class ChuwiMQTTBridge:
    def __init__(self, controller, face):
        self.controller = controller
        self.face = face

    def on_distance_message(self, payload):
        try:
            distance = float(payload)
        except ValueError:
            return

        if distance <= DISTANCE_LIMIT:
            self.controller.change_state("DETECTED")
            self.face.change_expression("WELCOME")
        else:
            self.controller.change_state("IDLE")
            self.face.change_expression("IDLE")

    def handle_message(self, topic, message):
        self.on_distance_message(message.decode())
