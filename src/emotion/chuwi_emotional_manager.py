from src.emotion.chuwi_emotional_adaptation import ChuwiEmotionalAdaptation
from src.emotion.emotion_database import EmotionDatabase


class ChuwiEmotionalManager:
    """Coordina deteccion emocional, base de conocimiento y estrategia de interaccion."""

    EMOTION_DB_MAP = {
        "ANXIOUS": "anxiety",
    }

    def __init__(self):
        self.adapter = ChuwiEmotionalAdaptation()
        self.database = EmotionDatabase()

    def analyze_interaction(self, message):
        emotion = self.adapter.detect_emotion(message)
        database_emotion = self.EMOTION_DB_MAP.get(emotion, emotion.lower())
        strategy = self.database.get_strategy(database_emotion)
        return {"emotion": emotion, "strategy": strategy}
