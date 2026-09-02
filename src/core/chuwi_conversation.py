from src.emotion.chuwi_emotional_manager import ChuwiEmotionalManager


class ChuwiConversation:
    def __init__(self, memory=None, emotional_manager=None, ai_engine=None):
        self.context = {}
        self.memory = memory
        self.emotional_manager = emotional_manager or ChuwiEmotionalManager()
        self.ai_engine = ai_engine

    def analyze_intent(self, message):
        text = message.lower()
        if any(word in text for word in ["hola", "buenos días", "buenas"]):
            return "greeting"
        if any(word in text for word in ["triste", "mal", "llorar", "miedo", "asustado"]):
            return "emotion"
        if any(word in text for word in ["jugar", "juego"]):
            return "play"
        if any(word in text for word in ["aprender", "tarea", "pregunta"]):
            return "learning"
        return "conversation"

    def build_context(self, user_name=None):
        context = {}
        if self.memory:
            user = self.memory.get_user()
            context["profile"] = user
            context["history"] = user.get("history", [])
        if user_name:
            context["user_name"] = user_name
        return context

    def generate_response(self, message, user_name=None):
        if self.memory:
            self.memory.remember(message)
        context = self.build_context(user_name)
        if self.ai_engine:
            return self.ai_engine.generate_response(message, context)
        return "Cuéntame más, quiero escucharte."
