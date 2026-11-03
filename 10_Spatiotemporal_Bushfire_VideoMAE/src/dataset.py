"""
Spatiotemporal PyTorch Dataset Loader for Northern Ghana Bushfire Forecasting.
Loads multi-epoch .npz tensor cubes containing:
- 5 observation days (t-4, t-3, t-2, t-1, t)
- 11 multimodal channels (VIIRS, Sentinel-2, ERA5-Land, SRTM)
- Target: next-day (t+24h) binary active fire mask
"""

import os
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader

class SavannahBushfireDataset(Dataset):
    """
    Spatiotemporal Dataset for VideoMAEv2 Cross-Modal Bushfire Forecasting.
    Yields:
        x: (Time=5, Channels=11, H=224, W=224)
        y: (1, H=224, W=224) target active fire mask at t+24h
    """
    def __init__(self, tensor_files, transform=None):
        self.tensor_files = tensor_files
        self.transform = transform

    def __len__(self):
        return len(self.tensor_files)

    def __getitem__(self, idx):
        file_path = self.tensor_files[idx]
        if os.path.exists(file_path):
            data = np.load(file_path)
            x = data["x"]  # (5, 11, 224, 224)
            y = data["y"]  # (1, 224, 224)
        else:
            # Deterministic mock tensor for pipeline testing / validation
            np.random.seed(idx)
            x = np.random.randn(5, 11, 224, 224).astype(np.float32)
            # Sparse fire target (< 1.5% active pixels)
            y = (np.random.rand(1, 224, 224) > 0.985).astype(np.float32)

        x_tensor = torch.from_numpy(x).float()
        y_tensor = torch.from_numpy(y).float()

        if self.transform:
            x_tensor, y_tensor = self.transform(x_tensor, y_tensor)

        return x_tensor, y_tensor

def get_dataloader(file_list, batch_size=4, shuffle=True, num_workers=0):
    dataset = SavannahBushfireDataset(file_list)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)

if __name__ == "__main__":
    print("Testing SavannahBushfireDataset loader...")
    dummy_files = [f"mock_cube_{i}.npz" for i in range(8)]
    loader = get_dataloader(dummy_files, batch_size=2)
    for batch_x, batch_y in loader:
        print(f"Batch X Shape: {batch_x.shape} (B, T, C, H, W)")
        print(f"Batch Y Shape: {batch_y.shape} (B, 1, H, W)")
        print(f"Fire pixel ratio in target: {(batch_y > 0).float().mean().item()*100:.2f}%")
        break
