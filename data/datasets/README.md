# Chuwi Emotional Datasets

## Objetivo
Documentación de datasets utilizados para entrenar y evaluar el sistema de inteligencia emocional multimodal de Chuwi.

## Modalidades

### 1. Facial Emotion
- Tipo: imágenes/videos faciales.
- Uso: detección de emociones mediante visión computacional.
- Emociones objetivo:
  - HAPPY
  - SAD
  - FEAR
  - ANGER
  - NEUTRAL

### 2. Voice Emotion
- Tipo: audio infantil.
- Uso: análisis de características vocales.
- Variables:
  - tono
  - intensidad
  - pausas
  - patrones de voz

### 3. Text Emotion
- Tipo: frases o conversaciones etiquetadas.
- Uso: clasificación emocional mediante NLP.

## Adaptación para Chuwi
Las etiquetas originales de los datasets serán mapeadas a estados útiles para apoyo pediátrico:

- FEAR → miedo a procedimientos médicos
- SAD → tristeza por hospitalización
- ANXIETY → ansiedad médica
- CALM → estado tranquilo
- HAPPY → interacción positiva

## Nota
Los datasets externos no se almacenan directamente en este repositorio por tamaño y licencia. Se incluirán scripts de carga, referencias y archivos de configuración necesarios.