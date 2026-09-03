"""
Integration layer between detected emotions and Chuwi personality behavior.

Receives multimodal emotion states and adapts personality responses.
"""


class ChuwiPersonalityIntegration:
    def __init__(self, personality=None):
        self.personality = personality

    def adapt_behavior(self, emotion: str, confidence: float = 0.0):
        profiles = {
            "SAD": {
                "tone": "gentle",
                "face": "empathetic",
                "action": "offer_support",
            },
            "FEAR": {
                "tone": "calm",
                "face": "reassuring",
                "action": "reduce_anxiety",
            },
            "HAPPY": {
                "tone": "energetic",
                "face": "smile",
                "action": "encourage_interaction",
            },
            "ANGER": {
                "tone": "patient",
                "face": "neutral",
                "action": "deescalate",
            },
            "CALM": {
                "tone": "friendly",
                "face": "neutral",
                "action": "continue_interaction",
            },
        }

        result = profiles.get(emotion, profiles["CALM"])
        result["confidence"] = confidence
        return result
