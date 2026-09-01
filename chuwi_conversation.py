from chuwi_emotional_manager import ChuwiEmotionalManager


class ChuwiConversation:
    def __init__(self, memory=None, emotional_manager=None):
        self.context = {}
        self.memory = memory
        self.emotional_manager = emotional_manager or ChuwiEmotionalManager()

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

    def generate_response(self, message, user_name=None):
        intent = self.analyze_intent(message)
        emotional_state = self.emotional_manager.analyze_interaction(message)

        if self.memory:
            self.memory.remember(message)
            user = self.memory.get_user()
            if user_name is None:
                user_name = user.get("name")

        if intent == "greeting":
            name = user_name if user_name else "amigo"
            return f"Hola {name}, me alegra verte. ¿Cómo estás hoy?"

        if emotional_state["emotion"] in ["fear", "anxiety"]:
            return "Estoy contigo. Podemos hablar de lo que sientes y hacerlo paso a paso."

        if intent == "emotion":
            return "Estoy aquí contigo. Puedes contarme cómo te sientes y qué pasó."

        if intent == "play":
            return "Podemos jugar juntos. ¿Qué juego te gustaría hacer hoy?"

        if intent == "learning":
            return "Vamos a aprender juntos paso a paso."

        return "Cuéntame más, quiero escucharte."