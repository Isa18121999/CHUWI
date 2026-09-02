# FERAC — Facial Emotion Dataset

## Purpose in Chuwi

FERAC is used as the first facial-expression dataset for Chuwi's visual emotion module.

The dataset supplied for this project contains four classes:

- `Natural`
- `joy`
- `fear`
- `anger`

## Local structure

```text
FERAC Dataset/
├── train/
│   ├── Natural/
│   ├── joy/
│   ├── fear/
│   └── anger/
└── test/
    ├── Natural/
    ├── joy/
    ├── fear/
    └── anger/
```

The supplied archive contains **615 training images** and **155 test images** (770 total).

| Split | Natural | Joy | Fear | Anger | Total |
|---|---:|---:|---:|---:|---:|
| Train | 147 | 370 | 39 | 59 | 615 |
| Test | 37 | 93 | 10 | 15 | 155 |
| Total | 184 | 463 | 49 | 74 | 770 |

## Important: class imbalance

`joy` is the majority class while `fear` is the minority class. Training must therefore use class-weighted loss and report per-class precision, recall and F1 rather than accuracy alone.

## Repository policy

The original face images are **not committed to this repository**. Keep the downloaded/extracted dataset outside Git and place it locally under:

```text
/mnt/data/FERAC Dataset/
```

or another local path supplied to the training script.

This avoids redistributing participant images and keeps the repository lightweight. Follow the dataset provider's terms and any applicable research/ethics requirements.

## Chuwi label mapping

FERAC labels remain unchanged during model training. The multimodal layer can map them to Chuwi's canonical emotional states:

| FERAC | Chuwi state |
|---|---|
| Natural | CALM |
| joy | HAPPY |
| fear | FEAR |
| anger | FRUSTRATED |

The mapping is performed **after** facial inference, not by modifying the ground-truth labels.

## Training

Use:

```bash
python scripts/train_ferac.py --data-dir "/path/to/FERAC Dataset"
```

The script creates a local model checkpoint and an evaluation report. Generated model files and metrics are intentionally kept out of Git unless explicitly selected as release artifacts.
