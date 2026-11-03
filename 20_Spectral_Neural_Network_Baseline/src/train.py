"""
Training and Evaluation Pipeline for Spectral Baselines (PyTorch MLP vs Scikit-Learn RF)
Emmanuel Yerbo | GeoAI Baseline Engine
"""

import os
import argparse
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, cohen_kappa_score, classification_report,
    confusion_matrix, f1_score
)
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from model import SpectralMLP, create_sklearn_mlp, create_random_forest

CLASS_NAMES = ["Water", "Bare", "Vegetation", "BuiltUp"]


def generate_benchmark_spectral_data(n_samples: int = 5000, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Synthesizes authentic Sentinel-2 surface reflectance distributions [B2 (Blue), B3 (Green), B4 (Red), B8 (NIR)]
    grounded in empirical radiometry across Ghanaian biomes.
    """
    rng = np.random.RandomState(random_state)
    n_per_class = n_samples // 4

    # Class 0: Water (High absorption in NIR, peak in Blue/Green)
    water_blue = rng.normal(0.065, 0.012, n_per_class)
    water_green = rng.normal(0.052, 0.010, n_per_class)
    water_red = rng.normal(0.035, 0.008, n_per_class)
    water_nir = rng.normal(0.015, 0.005, n_per_class)
    water = np.column_stack([water_blue, water_green, water_red, water_nir])

    # Class 1: Bare Soil (Rising spectral curve into NIR)
    bare_blue = rng.normal(0.180, 0.025, n_per_class)
    bare_green = rng.normal(0.220, 0.028, n_per_class)
    bare_red = rng.normal(0.275, 0.032, n_per_class)
    bare_nir = rng.normal(0.330, 0.035, n_per_class)
    bare = np.column_stack([bare_blue, bare_green, bare_red, bare_nir])

    # Class 2: Dense Vegetation (Chlorophyll absorption in Red, sharp Red-Edge jump into NIR)
    veg_blue = rng.normal(0.032, 0.006, n_per_class)
    veg_green = rng.normal(0.088, 0.012, n_per_class)
    veg_red = rng.normal(0.041, 0.007, n_per_class)
    veg_nir = rng.normal(0.485, 0.045, n_per_class)
    veg = np.column_stack([veg_blue, veg_green, veg_red, veg_nir])

    # Class 3: Built-Up Urban Fabric (Flat/moderate reflectance, spectrally confounded with bare soil)
    urb_blue = rng.normal(0.170, 0.022, n_per_class)
    urb_green = rng.normal(0.195, 0.024, n_per_class)
    urb_red = rng.normal(0.210, 0.026, n_per_class)
    urb_nir = rng.normal(0.235, 0.030, n_per_class)
    urban = np.column_stack([urb_blue, urb_green, urb_red, urb_nir])

    X = np.vstack([water, bare, veg, urban])
    X = np.clip(X, 0.001, 0.999)
    y = np.concatenate([
        np.zeros(n_per_class, dtype=np.int64),
        np.ones(n_per_class, dtype=np.int64),
        np.full(n_per_class, 2, dtype=np.int64),
        np.full(n_per_class, 3, dtype=np.int64)
    ])

    indices = rng.permutation(len(X))
    return X[indices], y[indices]


def train_pytorch_mlp(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    device: str = "cpu"
) -> Tuple[nn.Module, Dict[str, list]]:
    """
    Trains PyTorch SpectralMLP with Cross-Entropy Loss and Adam optimizer.
    """
    model = SpectralMLP(in_features=X_train.shape[1], hidden_dims=[64, 128, 64, 32], num_classes=4).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.long))
    val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.long))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    history = {"train_loss": [], "val_loss": [], "val_acc": []}

    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item() * len(bx)
        
        train_loss = total_train_loss / len(train_ds)

        model.eval()
        total_val_loss = 0.0
        correct = 0
        with torch.no_grad():
            for bx, by in val_loader:
                bx, by = bx.to(device), by.to(device)
                logits = model(bx)
                loss = criterion(logits, by)
                total_val_loss += loss.item() * len(bx)
                preds = torch.argmax(logits, dim=1)
                correct += (preds == by).sum().item()

        val_loss = total_val_loss / len(val_ds)
        val_acc = correct / len(val_ds)
        scheduler.step(val_loss)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        if epoch % 10 == 0 or epoch == epochs:
            print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}%")

    return model, history


def evaluate_classifier(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics."""
    acc = accuracy_score(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro')
    weighted_f1 = f1_score(y_true, y_pred, average='weighted')
    cm = confusion_matrix(y_true, y_pred)

    print(f"\n==================== {name} Evaluation ====================")
    print(f"Overall Accuracy: {acc*100:.2f}% | Cohen's Kappa: {kappa:.4f} | Macro F1: {macro_f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4))
    print("Confusion Matrix:")
    print(cm)
    return {
        "accuracy": acc,
        "kappa": kappa,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "confusion_matrix": cm
    }


def main():
    parser = argparse.ArgumentParser(description="Train Spectral Pixel Baseline")
    parser.add_argument("--samples", type=int, default=5000, help="Number of benchmark samples")
    parser.add_argument("--epochs", type=int, default=40, help="Number of PyTorch training epochs")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running Spectral Baseline Engine on device: {device}")

    # Generate benchmark radiometric samples
    X, y = generate_benchmark_spectral_data(n_samples=args.samples)
    
    # Train / Val / Test Split (70 / 15 / 15)
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1765, stratify=y_train_val, random_state=42)

    # Standardize spectral features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # 1. Train Random Forest Baseline
    print("\n[1/3] Training Random Forest Baseline...")
    rf = create_random_forest()
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_results = evaluate_classifier("Random Forest", y_test, rf_preds)

    # 2. Train Scikit-Learn MLP Baseline (Matching Notebook)
    print("\n[2/3] Training Scikit-Learn MLP (16, 32, 8)...")
    sk_mlp = create_sklearn_mlp()
    sk_mlp.fit(X_train_scaled, y_train)
    sk_mlp_preds = sk_mlp.predict(X_test_scaled)
    sk_mlp_results = evaluate_classifier("Scikit-Learn MLP (16,32,8)", y_test, sk_mlp_preds)

    # 3. Train PyTorch Deep SpectralMLP
    print("\n[3/3] Training PyTorch Deep SpectralMLP (64, 128, 64, 32)...")
    torch_mlp, history = train_pytorch_mlp(
        X_train_scaled, y_train, X_val_scaled, y_val,
        epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, device=device
    )
    torch_mlp.eval()
    with torch.no_grad():
        test_logits = torch_mlp(torch.tensor(X_test_scaled, dtype=torch.float32).to(device))
        torch_preds = torch.argmax(test_logits, dim=1).cpu().numpy()
    torch_mlp_results = evaluate_classifier("PyTorch Deep SpectralMLP", y_test, torch_preds)

    # Summary Ablation Table
    print("\n" + "="*70)
    print("               SUMMARY SPECTRAL ABLATION MATRIX")
    print("="*70)
    print(f"{'Model Architecture':<30} | {'OA (%)':<8} | {'Kappa':<8} | {'Macro F1':<8}")
    print("-" * 70)
    print(f"{'Random Forest (100 trees)':<30} | {rf_results['accuracy']*100:<8.2f} | {rf_results['kappa']:<8.4f} | {rf_results['macro_f1']:<8.4f}")
    print(f"{'Sklearn MLP (16, 32, 8)':<30} | {sk_mlp_results['accuracy']*100:<8.2f} | {sk_mlp_results['kappa']:<8.4f} | {sk_mlp_results['macro_f1']:<8.4f}")
    print(f"{'PyTorch Deep SpectralMLP':<30} | {torch_mlp_results['accuracy']*100:<8.2f} | {torch_mlp_results['kappa']:<8.4f} | {torch_mlp_results['macro_f1']:<8.4f}")
    print("="*70)


if __name__ == "__main__":
    main()
