# Chuwi Facial Camera Pipeline

```text
Camera
  ↓
Face Detection (OpenCV)
  ↓
224x224 preprocessing
  ↓
FacialEmotionModel
  ↓
FacialRuntime
  ↓
MultimodalEmotionFusion
  ↓
Adaptive Chuwi response
```

The facial module provides emotion, confidence and source metadata for fusion with voice and text signals.
