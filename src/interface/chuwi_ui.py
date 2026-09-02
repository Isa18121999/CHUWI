class ChuwiUI:

    def __init__(self):
        self.current_state = "IDLE"

    def update_state(self, state):
        self.current_state = state
        self.render()

    def show_state(self, state):
        self.update_state(state)

    def render(self):
        screens = {
            "IDLE": "Chuwi esperando...",
            "DETECTED": "Hola, me alegra conocerte",
            "WELCOME": "Bienvenido a Chuwi",
            "LISTENING": "Te estoy escuchando",
            "THINKING": "Chuwi está pensando",
            "RESPONDING": "Chuwi está respondiendo"
        }
        print(screens.get(self.current_state, "Chuwi activo"))
