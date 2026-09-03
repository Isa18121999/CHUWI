class FacialEmotionAdapter:
    def __init__(self, model):
        self.model = model

    def predict(self, face_tensor):
        output = self.model(face_tensor)
        probabilities = output.softmax(dim=1)
        confidence, index = probabilities.max(dim=1)

        return {
            "emotion": self.model.classes[index.item()],
            "confidence": float(confidence.item()),
            "scores": probabilities.detach().cpu().numpy().tolist()[0],
        }
