"""
Model Architectures for Pixel-Based Spectral Classification
Emmanuel Yerbo | GeoAI Baseline Engine
"""

import torch
import torch.nn as nn
from typing import List, Optional
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier


class SpectralMLP(nn.Module):
    """
    Deep Multilayer Perceptron (MLP) for Pixel-Based Multi-Spectral Classification.
    
    Operates on radiometric spectral vectors x in R^C across C satellite bands
    (e.g., Sentinel-2 B2, B3, B4, B8 or VNIR-SWIR channels).
    """
    def __init__(
        self,
        in_features: int = 4,
        hidden_dims: Optional[List[int]] = None,
        num_classes: int = 4,
        dropout: float = 0.15
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [64, 128, 64, 32]
        
        layers = []
        prev_dim = in_features
        for h_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, h_dim))
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.ReLU(inplace=True))
            if dropout > 0:
                layers.append(nn.Dropout(p=dropout))
            prev_dim = h_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        self.network = nn.Sequential(*layers)
        self.in_features = in_features
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Args:
            x: Tensor of shape (batch_size, in_features)
        Returns:
            logits: Tensor of shape (batch_size, num_classes)
        """
        return self.network(x)


def create_sklearn_mlp(
    hidden_layer_sizes=(16, 32, 8),
    max_iter=1000,
    random_state=42
) -> MLPClassifier:
    """
    Instantiates Scikit-Learn Multilayer Perceptron baseline matching notebook architecture.
    """
    return MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        max_iter=max_iter,
        activation='relu',
        solver='adam',
        random_state=random_state,
        verbose=False
    )


def create_random_forest(
    n_estimators=100,
    max_depth=15,
    random_state=42
) -> RandomForestClassifier:
    """
    Instantiates Scikit-Learn Random Forest ensemble baseline.
    """
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
