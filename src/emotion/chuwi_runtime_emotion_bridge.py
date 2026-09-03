"""
Bridge between Chuwi runtime and emotional modules.

Flow:
facial/voice/text emotion -> fusion -> personality -> response
"""

class ChuwiRuntimeEmotionBridge:
    def __init__(self, fusion, personality, face):
        self.fusion = fusion
        self.personality = personality
        self.face = face

    def process_emotion(self, signals):
        state = self.fusion.combine(signals)
        behavior = self.personality.adapt(state)
        expression = self.face.set_emotion(state)

        return {
            "emotion": state,
            "behavior": behavior,
            "expression": expression,
        }
