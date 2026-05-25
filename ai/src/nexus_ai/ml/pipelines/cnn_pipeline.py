"""
PyTorch Pipeline managing CNN training and inference.
"""
from __future__ import annotations

import os
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from nexus_ai.ml.vision.cnn_model import ProspectivityCNN
from nexus_ai.ml.vision.dataset import MultispectralDataset


class CNNPipeline:
    """
    Manages the PyTorch model lifecycle: training loop, validation, 
    checkpointing, and inference execution.
    """

    def __init__(self, in_channels: int, device: str | None = None):
        self.in_channels = in_channels
        
        # Automatically select GPU if available and not explicitly requested
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)
            
        self.model = ProspectivityCNN(in_channels=in_channels).to(self.device)
        self._is_trained = False

    def train(
        self, 
        train_loader: DataLoader, 
        val_loader: DataLoader | None = None,
        epochs: int = 20, 
        learning_rate: float = 1e-3
    ) -> list[float]:
        """
        Standard PyTorch training loop.
        Returns a list of average losses per epoch.
        """
        # Pos_weight can be added here if classes are imbalanced
        criterion = nn.BCEWithLogitsLoss()
        optimizer = Adam(self.model.parameters(), lr=learning_rate)
        
        epoch_losses = []

        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            
            for batch_idx, (inputs, targets) in enumerate(train_loader):
                inputs = inputs.to(self.device)
                targets = targets.unsqueeze(1).to(self.device) # Shape [Batch, 1]

                optimizer.zero_grad()
                
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                
            avg_loss = running_loss / len(train_loader)
            epoch_losses.append(avg_loss)
            
            # Simple print for logging; in prod this goes to structlog/TensorBoard/MLflow
            print(f"Epoch [{epoch+1}/{epochs}] - Loss: {avg_loss:.4f}")
            
            # Optional validation phase
            if val_loader:
                val_loss, val_acc = self.evaluate(val_loader)
                print(f"  -> Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        self._is_trained = True
        return epoch_losses

    @torch.no_grad()
    def evaluate(self, val_loader: DataLoader) -> tuple[float, float]:
        """Evaluate the model on a validation DataLoader."""
        self.model.eval()
        criterion = nn.BCEWithLogitsLoss()
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, targets in val_loader:
            inputs = inputs.to(self.device)
            targets = targets.unsqueeze(1).to(self.device)
            
            outputs = self.model(inputs)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item()
            
            # Convert logits to probabilities, then to 0/1 predictions
            probs = torch.sigmoid(outputs)
            preds = (probs > 0.5).float()
            
            correct += (preds == targets).sum().item()
            total += targets.size(0)
            
        return total_loss / len(val_loader), correct / total

    @torch.no_grad()
    def predict(self, inference_loader: DataLoader) -> tuple[list[float], list[int]]:
        """
        Run inference on new data.
        Returns: (probabilities, binary_predictions)
        """
        if not self._is_trained:
            raise RuntimeError("Model must be trained or loaded before inference.")
            
        self.model.eval()
        
        all_probs = []
        all_preds = []
        
        for inputs, _ in inference_loader:
            inputs = inputs.to(self.device)
            outputs = self.model(inputs)
            
            probs = torch.sigmoid(outputs).cpu().numpy().flatten()
            preds = (probs > 0.5).astype(int).tolist()
            
            all_probs.extend(probs.tolist())
            all_preds.extend(preds)
            
        return all_probs, all_preds

    def save(self, filepath: str | Path) -> None:
        """Save the model architecture details and weights using standard torch.save."""
        if not self._is_trained:
            raise RuntimeError("Cannot save an untrained model.")
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        checkpoint = {
            "in_channels": self.in_channels,
            "state_dict": self.model.state_dict(),
        }
        torch.save(checkpoint, filepath)

    @classmethod
    def load(cls, filepath: str | Path, device: str | None = None) -> CNNPipeline:
        """Load a trained PyTorch model from disk."""
        checkpoint = torch.load(filepath, map_location="cpu") # Load to CPU first
        
        instance = cls(in_channels=checkpoint["in_channels"], device=device)
        instance.model.load_state_dict(checkpoint["state_dict"])
        instance._is_trained = True
        
        return instance
