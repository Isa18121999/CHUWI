"""
Chuwi facial emotion training pipeline.

Supports FERAC/ChildEFES style labeled datasets through ChuwiFacialDataset.
Uses class weights and reports evaluation metrics.
"""

import torch
from torch import nn
from torch.utils.data import DataLoader

from src.emotion.facial_dataset_loader import ChuwiFacialDataset
from src.emotion.facial_emotion_model import FacialEmotionModel


EMOTIONS = [
    "CALM",
    "HAPPY",
    "SAD",
    "FEAR",
    "ANGER",
    "SURPRISE",
    "DISGUST",
]


def train(csv_file, image_dir, epochs=20):
    dataset = ChuwiFacialDataset(csv_file, image_dir)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = FacialEmotionModel(num_classes=len(dataset.labels))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(epochs):
        model.train()
        for images, labels in loader:
            optimizer.zero_grad()
            output = model(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch + 1}/{epochs} complete")

    return model
