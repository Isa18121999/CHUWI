class ChuwiInteractionState:
    """Estados de interacción de Chuwi sin pantalla física.

    Chuwi expresa estados mediante voz, conversación y comportamiento
    afectivo, no mediante una interfaz visual.
    """

    def __init__(self):
        self.current_state = "IDLE"

    def update_state(self, state):
        self.current_state = state
        return self.get_state_message()

    def show_state(self, state):
        return self.update_state(state)

    def get_state_message(self):
        states = {
            "IDLE": "Chuwi está esperando interacción",
            "DETECTED": "Chuwi detectó presencia cercana",
            "WELCOME": "Chuwi está listo para saludar",
            "LISTENING": "Chuwi está escuchando",
            "THINKING": "Chuwi está procesando información",
            "RESPONDING": "Chuwi está generando una respuesta"
        }
        return states.get(self.current_state, "Chuwi activo")
