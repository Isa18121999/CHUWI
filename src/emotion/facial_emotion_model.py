from pathlib import Path

import torch
from torch import nn
from torchvision import transforms
from PIL import Image


class FacialEmotionCNN(nn.Module):
    """Compact CNN baseline for the four FERAC facial-emotion classes."""

    CLASSES = ("Natural", "joy", "fear", "anger")

    def __init__(self, num_classes=4):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.30),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


class FacialEmotionModel:
    """Inference wrapper used by Chuwi's visual emotion pipeline."""

    def __init__(self, checkpoint=None, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = FacialEmotionCNN(len(FacialEmotionCNN.CLASSES)).to(self.device)
        if checkpoint:
            checkpoint_path = Path(checkpoint)
            state = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(state["model_state_dict"] if "model_state_dict" in state else state)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    @torch.inference_mode()
    def predict(self, image):
        """Return emotion, confidence and class probabilities for one RGB image."""
        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        else:
            image = image.convert("RGB")

        tensor = self.transform(image).unsqueeze(0).to(self.device)
        probabilities = torch.softmax(self.model(tensor), dim=1)[0]
        index = int(torch.argmax(probabilities))

        scores = {
            label: float(probabilities[i])
            for i, label in enumerate(FacialEmotionCNN.CLASSES)
        }
        return {
            "emotion": FacialEmotionCNN.CLASSES[index],
            "confidence": float(probabilities[index]),
            "scores": scores,
        }
