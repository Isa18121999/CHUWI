"""Prepara FERAC para reconocimiento facial.

Detecta el rostro principal de cada imagen, lo recorta con margen,
redimensiona a 224x224 y conserva las clases originales.

Uso:
    python scripts/prepare_ferac_faces.py --input <FERAC_DIR> --output <OUTPUT_DIR>
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2


CLASSES = ("Natural", "joy", "fear", "anger")


def crop_largest_face(image, detector):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=5,
        minSize=(40, 40),
    )
    if len(faces) == 0:
        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(30, 30),
        )
    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    padding = int(0.22 * max(w, h))
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + w + padding)
    y2 = min(image.shape[0], y + h + padding)

    crop = image[y1:y2, x1:x2]
    return cv2.resize(crop, (224, 224), interpolation=cv2.INTER_AREA)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    if detector.empty():
        raise RuntimeError("No se pudo cargar el detector facial de OpenCV")

    total = 0
    retained = 0
    for class_name in CLASSES:
        source_dir = args.input / class_name
        output_dir = args.output / class_name
        output_dir.mkdir(parents=True, exist_ok=True)

        for source in sorted(source_dir.glob("*.jpg")):
            total += 1
            image = cv2.imread(str(source))
            if image is None:
                continue
            crop = crop_largest_face(image, detector)
            if crop is None:
                continue
            target = output_dir / source.name
            cv2.imwrite(str(target), crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
            retained += 1

    print(f"Imágenes procesadas: {total}")
    print(f"Rostros conservados: {retained}")
    print(f"Sin detección facial: {total - retained}")


if __name__ == "__main__":
    main()
