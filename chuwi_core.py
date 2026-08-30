from chuwi_controller import ChuwiController
from chuwi_face import ChuwiFace
from chuwi_personality import ChuwiPersonality
from memory_manager import ChuwiMemory


class ChuwiCore:
    def __init__(self):
        self.controller = ChuwiController()
        self.face = ChuwiFace()
        self.personality = ChuwiPersonality()
        self.memory = ChuwiMemory()

    def update_distance(self, distance):
        self.controller.update_distance(distance)
        self.face.change_expression(self.controller.state)

    def respond(self, message):
        self.memory.remember(message)
        return self.personality.style_response(message)
