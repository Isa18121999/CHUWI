from chuwi_emotional_adaptation import ChuwiEmotionalAdaptation


class ChuwiEmotionalManager:
    """Coordina detección emocional y estrategia de interacción de Chuwi."""

    def __init__(self):
        self.adapter = ChuwiEmotionalAdaptation()

    def analyze_interaction(self, message):
        emotion = self.adapter.detect_emotion(message)
        strategy = self.adapter.select_strategy(emotion)

        return {
            "emotion": emotion,
            "strategy": strategy
        }
