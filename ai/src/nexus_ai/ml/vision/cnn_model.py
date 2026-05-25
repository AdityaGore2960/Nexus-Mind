"""
CNN Architecture for Multispectral Images.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ProspectivityCNN(nn.Module):
    """
    A custom Convolutional Neural Network designed to handle N-band 
    multispectral satellite patches (e.g., 256x256x12) for binary 
    mineral prospectivity classification.
    """
    
    def __init__(self, in_channels: int, dropout_rate: float = 0.3):
        super().__init__()
        
        # Block 1
        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        # Block 2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        # Block 3
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # Block 4
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        
        # Global Average Pooling collapses Spatial Dimensions (H,W) -> (1,1)
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classification Head
        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(256, 64)
        self.fc2 = nn.Linear(64, 1)  # Binary output (logits)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Expected input shape: (Batch, Channels, Height, Width)
        
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = F.relu(self.bn4(self.conv4(x)))
        
        x = self.global_pool(x)
        x = torch.flatten(x, 1)  # Flatten all dimensions except batch
        
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        
        # We output raw logits. BCEWithLogitsLoss combines Sigmoid + BCELoss for numerical stability.
        return x
