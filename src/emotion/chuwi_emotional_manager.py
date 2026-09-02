from src.emotion.chuwi_emotional_adaptation import ChuwiEmotionalAdaptation
from emotion_database import EmotionDatabase


class ChuwiEmotionalManager:
    """Coordina deteccion emocional, base de conocimiento y estrategia de interaccion."""

    def __init__(self):
        self.adapter = ChuwiEmotionalAdaptation()
        self.database = EmotionDatabase()

    def analyze_interaction(self, message):
        emotion = self.adapter.detect_emotion(message)
        strategy = self.database.get_strategy(emotion)
        return {"emotion": emotion, "strategy": strategy}
