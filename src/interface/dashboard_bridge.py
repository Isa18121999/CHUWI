class ChuwiDashboardBridge:
    def __init__(self):
        self.current_view = "IDLE"

    def update(self, state):
        self.current_view = state
        views = {
            "IDLE": "Chuwi esperando...",
            "DETECTED": "Hola, me alegra conocerte",
            "WELCOME": "Bienvenido a Chuwi",
            "LISTENING": "Te estoy escuchando",
            "THINKING": "Chuwi está pensando",
            "RESPONDING": "Chuwi está respondiendo"
        }
        return views.get(state, "Chuwi activo")
