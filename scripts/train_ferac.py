import argparse
import json
from pathlib import Path

import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.emotion.facial_emotion_model import FacialEmotionCNN


CLASSES = list(FacialEmotionCNN.CLASSES)


def build_loaders(data_dir, batch_size):
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    root = Path(data_dir)
    train = datasets.ImageFolder(root / "train", transform=train_transform)
    test = datasets.ImageFolder(root / "test", transform=test_transform)

    expected = set(CLASSES)
    if set(train.classes) != expected or set(test.classes) != expected:
        raise ValueError(
            f"FERAC classes do not match expected classes. "
            f"train={train.classes}, test={test.classes}, expected={CLASSES}"
        )

    return (
        train,
        test,
        DataLoader(train, batch_size=batch_size, shuffle=True, num_workers=0),
        DataLoader(test, batch_size=batch_size, shuffle=False, num_workers=0),
    )


def evaluate(model, loader, device):
    model.eval()
    y_true, y_pred = [], []
    with torch.inference_mode():
        for images, labels in loader:
            logits = model(images.to(device))
            predictions = logits.argmax(dim=1).cpu().tolist()
            y_pred.extend(predictions)
            y_true.extend(labels.tolist())

    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(CLASSES))),
        target_names=CLASSES,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASSES))))
    return report, matrix.tolist()


def main():
    parser = argparse.ArgumentParser(description="Train Chuwi's FERAC facial-emotion baseline")
    parser.add_argument("--data-dir", required=True, help="Path to the extracted FERAC Dataset directory")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--output-dir", default="models/ferac")
    args = parser.parse_args()

    train_set, test_set, train_loader, test_loader = build_loaders(args.data_dir, args.batch_size)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FacialEmotionCNN(len(CLASSES)).to(device)

    # Inverse-frequency weights reduce the bias toward Joy in FERAC.
    counts = torch.bincount(torch.tensor(train_set.targets), minlength=len(CLASSES)).float()
    weights = counts.sum() / (len(CLASSES) * counts)
    criterion = nn.CrossEntropyLoss(weight=weights.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    best_f1 = -1.0
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * labels.size(0)

        report, matrix = evaluate(model, test_loader, device)
        macro_f1 = report["macro avg"]["f1-score"]
        print(f"epoch={epoch:02d} loss={running_loss / len(train_set):.4f} macro_f1={macro_f1:.4f}")

        if macro_f1 > best_f1:
            best_f1 = macro_f1
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": CLASSES,
                    "best_macro_f1": best_f1,
                },
                output_dir / "ferac_cnn.pt",
            )
            (output_dir / "metrics.json").write_text(
                json.dumps({"classification_report": report, "confusion_matrix": matrix}, indent=2),
                encoding="utf-8",
            )

    print(f"best_macro_f1={best_f1:.4f}")
    print(f"checkpoint={output_dir / 'ferac_cnn.pt'}")


if __name__ == "__main__":
    main()
