from enum import Enum


class FaceState(Enum):
    IDLE = "idle"
    WELCOME = "welcome"
    LISTENING = "listening"
    THINKING = "thinking"
    HAPPY = "happy"
    SLEEP = "sleep"


class ChuwiFace:
    def __init__(self):
        self.state = FaceState.IDLE

    def change_expression(self, state):
        self.state = state
        return self.state.value

    def get_expression(self):
        return {
            "idle": "Esperando usuario",
            "welcome": "Hola, me alegra conocerte",
            "listening": "Te estoy escuchando",
            "thinking": "Estoy pensando",
            "happy": "Estoy feliz de ayudarte",
            "sleep": "Modo descanso"
        }.get(self.state.value, "")
