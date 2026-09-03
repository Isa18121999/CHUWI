"""
Chuwi Emotional Response Manager
Connects multimodal emotion outputs with adaptive robot behavior.
"""

EMOTION_ACTIONS = {
    "CALM": {"voice": "normal", "face": "neutral", "response": "friendly"},
    "HAPPY": {"voice": "joyful", "face": "smile", "response": "engaging"},
    "SAD": {"voice": "soft", "face": "empathetic", "response": "supportive"},
    "FEAR": {"voice": "calm", "face": "reassuring", "response": "comforting"},
    "ANGER": {"voice": "calm", "face": "neutral", "response": "deescalating"},
    "SURPRISE": {"voice": "curious", "face": "alert", "response": "interactive"},
    "DISGUST": {"voice": "gentle", "face": "neutral", "response": "supportive"},
}


def adapt_response(emotion: str):
    return EMOTION_ACTIONS.get(
        emotion.upper(),
        EMOTION_ACTIONS["CALM"]
    )
