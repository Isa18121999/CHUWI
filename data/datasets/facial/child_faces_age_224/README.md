# Child Faces Age 224

Dataset de adaptación facial infantil para Chuwi.

## Procesamiento realizado

- Extracción de rostros con OpenCV.
- Recorte del rostro principal.
- Normalización a 224x224 píxeles.
- Generación de labels.csv.

## Estructura

```
child_faces_age_224/
├── face_*.jpg
└── labels.csv
```

## Etiquetas

Este dataset no incluye etiquetas emocionales originales.

Campo emotion:
- unlabeled_emotion

Uso:
- adaptación del modelo facial a rostros infantiles.
- validación externa.
- no usar como dataset principal de clasificación emocional.
