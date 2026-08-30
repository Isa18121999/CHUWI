class ChuwiConversation:
    def __init__(self):
        self.context = {}

    def analyze_intent(self, message):
        text = message.lower()

        if any(word in text for word in ["hola", "buenos días", "buenas"]):
            return "greeting"
        if any(word in text for word in ["triste", "mal", "llorar"]):
            return "emotion"
        if any(word in text for word in ["jugar", "juego"]):
            return "play"
        if any(word in text for word in ["aprender", "tarea", "pregunta"]):
            return "learning"

        return "conversation"

    def generate_response(self, message, user_name=None):
        intent = self.analyze_intent(message)

        if intent == "greeting":
            name = user_name if user_name else "amigo"
            return f"Hola {name}, me alegra verte. ¿Cómo estás hoy?"

        if intent == "emotion":
            return "Estoy aquí para escucharte. ¿Quieres contarme qué pasó?"

        if intent == "play":
            return "Podemos jugar juntos. ¿Qué juego te gustaría hacer?"

        if intent == "learning":
            return "Vamos a aprender juntos paso a paso."

        return "Cuéntame más, quiero escucharte."
