"""Preprocess child facial dataset for Chuwi.

- Detects faces using OpenCV
- Crops the largest face
- Resizes to 224x224
- Generates labels.csv
"""

import cv2
import csv
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


def preprocess(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    labels = []
    index = 0

    for image_path in input_dir.rglob('*'):
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        image = cv2.imread(str(image_path))
        if image is None:
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            continue

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face = image[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))

        filename = f'face_{index:04d}.jpg'
        cv2.imwrite(str(output_dir / filename), face)

        labels.append([filename, 'unknown', 'unlabeled_emotion'])
        index += 1

    with open(output_dir / 'labels.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['image', 'age_group', 'emotion'])
        writer.writerows(labels)


if __name__ == '__main__':
    preprocess('data/raw/child_faces', 'data/datasets/facial/child_faces_age_224')
