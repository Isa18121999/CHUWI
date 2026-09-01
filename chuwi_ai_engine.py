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

        emotional_result = self.emotional_manager.analyze_interaction(message)
        emotional_state = emotional_result["emotion"]
        strategy = emotional_result["strategy"]

        name = context.get("profile", {}).get("name")
        greeting = f"Hola {name}, " if name else ""

        if emotional_state == "FEAR":
            return greeting + "Estoy contigo. Podemos hablar de lo que sientes y hacerlo paso a paso.", strategy

        if emotional_state == "SAD":
            return greeting + "Estoy aquí para escucharte. ¿Quieres contarme cómo te sientes?", strategy

        if emotional_state == "ANXIOUS":
            return greeting + "Podemos respirar juntos y conversar tranquilamente.", strategy

        if "hola" in message.lower():
            return greeting + "me alegra verte. ¿Cómo estás hoy?", strategy

        return greeting + "Te estoy escuchando y quiero acompañarte.", strategy
