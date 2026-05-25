"""
PyTorch Dataset and Augmentation for Multispectral Satellite Imagery.
"""
from __future__ import annotations

import os

import numpy as np
import rasterio  # type: ignore[import-untyped]
import torch
from torch.utils.data import Dataset
import torchvision.transforms.v2 as transforms  # type: ignore[import-untyped]


class MultispectralDataset(Dataset):
    """
    Loads multi-band GeoTIFF patches for CNN training/inference.
    Expects data to be pre-tiled into smaller patches (e.g., 256x256).
    """

    def __init__(
        self, 
        image_paths: list[str], 
        labels: list[int] | None = None,
        is_training: bool = True
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.is_training = is_training
        
        # We use v2 transforms which cleanly support n-dimensional tensors, not just RGB PIL images.
        if self.is_training:
            self.transform = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.5),
                transforms.RandomApply([
                    transforms.GaussianBlur(kernel_size=3)
                ], p=0.2),
                # Note: Avoid color jitter as spectral signatures are absolute physical measurements
            ])
        else:
            self.transform = None

    def __len__(self) -> int:
        return len(self.image_paths)

    def _load_geotiff(self, path: str) -> np.ndarray:
        with rasterio.open(path) as src:
            # Read all bands; shape is (Bands, Height, Width)
            # We replace NaN with 0, a common padding value for nodata
            data = src.read()
            data = np.nan_to_num(data, nan=0.0)
            
            # Simple Min-Max scaling per band across the dataset is ideal,
            # but for simplicity we standardize using a pseudo-global max if known,
            # or standardize to mean=0, std=1 locally per patch.
            # Local normalization (Instance Norm):
            means = data.mean(axis=(1, 2), keepdims=True)
            stds = data.std(axis=(1, 2), keepdims=True) + 1e-7
            data = (data - means) / stds
            
            return data.astype(np.float32)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor | None]:
        path = self.image_paths[idx]
        
        # Load and convert to tensor (Channels, Height, Width)
        img_array = self._load_geotiff(path)
        img_tensor = torch.from_numpy(img_array)
        
        # Apply augmentations
        if self.transform:
            img_tensor = self.transform(img_tensor)
            
        if self.labels is not None:
            label = torch.tensor(self.labels[idx], dtype=torch.float32)
            return img_tensor, label
            
        return img_tensor, None
