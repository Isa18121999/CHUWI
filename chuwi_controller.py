from enum import Enum


class ChuwiState(Enum):
    IDLE = "Esperando"
    DETECTED = "Persona detectada"
    WELCOME = "Bienvenida"
    LISTENING = "Escuchando"
    THINKING = "Procesando"
    SPEAKING = "Respondiendo"


class ChuwiController:

    def __init__(self):
        self.state = ChuwiState.IDLE
        self.distance = None

    def update_distance(self, distance):
        self.distance = distance

        if distance <= 80:
            if self.state == ChuwiState.IDLE:
                self.change_state(ChuwiState.DETECTED)

        else:
            self.change_state(ChuwiState.IDLE)

    def start_welcome(self):
        self.change_state(ChuwiState.WELCOME)

    def start_listening(self):
        self.change_state(ChuwiState.LISTENING)

    def start_thinking(self):
        self.change_state(ChuwiState.THINKING)

    def start_speaking(self):
        self.change_state(ChuwiState.SPEAKING)

    def change_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state.value
