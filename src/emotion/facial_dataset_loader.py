import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class ChuwiFacialDataset(Dataset):
    def __init__(self, csv_file, image_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.image_dir = image_dir
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        self.labels = sorted(self.data['emotion'].unique())
        self.label_to_id = {label: i for i, label in enumerate(self.labels)}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        path = os.path.join(self.image_dir, row['image'])
        image = Image.open(path).convert('RGB')
        image = self.transform(image)
        label = self.label_to_id[row['emotion']]
        return image, label
