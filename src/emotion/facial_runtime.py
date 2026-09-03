"""
Chuwi realtime facial emotion runtime bridge.
Connects camera inference with the affective fusion layer.
"""

class FacialRuntime:
    def __init__(self, model, fusion=None):
        self.model = model
        self.fusion = fusion

    def process_face(self, face_tensor):
        result = self.model.predict(face_tensor)

        emotion_data = {
            "emotion": result.get("emotion"),
            "confidence": result.get("confidence", 0.0),
            "source": "facial"
        }

        if self.fusion:
            return self.fusion.update(emotion_data)

        return emotion_data
