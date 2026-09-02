from src.emotion.chuwi_emotional_adaptation import ChuwiEmotionalAdaptation
from src.emotion.emotion_database import EmotionDatabase
from src.emotion.multimodal_emotion_fusion import MultimodalEmotionFusion


class ChuwiEmotionalManager:
    """Coordina deteccion emocional, fusion multimodal y estrategias."""

    EMOTION_DB_MAP = {
        "ANXIOUS": "anxiety",
    }

    def __init__(self, fusion=None):
        self.adapter = ChuwiEmotionalAdaptation()
        self.database = EmotionDatabase()
        self.fusion = fusion or MultimodalEmotionFusion()

    def analyze_interaction(self, message, modalities=None):
        """Analiza texto y, opcionalmente, señales de voz y rostro.

        Si no se proporcionan modalidades adicionales, mantiene el flujo
        actual basado en texto para conservar compatibilidad.
        """
        text_emotion = self.adapter.detect_emotion(message)
        signals = {
            "text": {
                "emotion": text_emotion,
                "confidence": 1.0,
            }
        }
        signals.update(modalities or {})

        fused = self.fusion.fuse(signals)
        emotion = fused["emotion"]
        database_emotion = self.EMOTION_DB_MAP.get(emotion, emotion.lower())
        strategy = self.database.get_strategy(database_emotion)

        return {
            "emotion": emotion,
            "strategy": strategy,
            "confidence": fused["confidence"],
            "scores": fused["scores"],
        }
