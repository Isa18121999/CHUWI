from chuwi_emotional_manager import ChuwiEmotionalManager


class ChuwiAIEngine:
    """Motor base de inteligencia conversacional adaptativa de Chuwi."""

    def __init__(self):
        self.personality = {
            "name": "Chuwi",
            "style": "amable, paciente y motivador",
            "audience": "pacientes pediátricos"
        }
        self.emotional_manager = ChuwiEmotionalManager()

    def build_context(self, user_profile=None, conversation=None):
        return {
            "profile": user_profile or {},
            "conversation": conversation or []
        }

    def generate_response(self, message, context=None):
        context = context or {}

        emotional_state = self.emotional_manager.analyze(message)
        strategy = self.emotional_manager.get_strategy(emotional_state)

        if emotional_state == "FEAR":
            return "Estoy contigo. Podemos hablar de lo que sientes y hacerlo paso a paso.", strategy

        if emotional_state == "SAD":
            return "Estoy aquí para escucharte. ¿Quieres contarme cómo te sientes?", strategy

        if "hola" in message.lower():
            return "Hola, me alegra verte. ¿Cómo estás hoy?", strategy

        return "Te estoy escuchando y quiero acompañarte.", strategy
