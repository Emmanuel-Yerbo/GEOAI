"""
Dataset Ingestion and Multicollinearity Pruning for GAMA XAI LULC Pipeline
Emmanuel Yerbo | GeoAI & Remote Sensing Engineering
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split

CLASS_NAMES = {
    0: "Built-Up",
    1: "Vegetation",
    2: "Water",
    3: "Bare Soil"
}

CLASS_COLORS = {
    0: "#E8453C",   # Built-Up (red)
    1: "#1B7A2F",   # Vegetation (dark green)
    2: "#2196F3",   # Water (blue)
    3: "#9E9E9E"    # Bare Soil (grey)
}

# Highly collinear features (|r| > 0.95) pruned to ensure orthogonal game-theoretic SHAP attribution
COLS_TO_DROP = [
    'B2',         # Drop Blue (r = 0.9560 with Green B3) -> Keep B3
    'B5',         # Drop RedEdge-1 (r = 0.9539 with Red B4) -> Keep B4
    'B6',         # Drop RedEdge-2 (r = 0.9787 with NIR B8) -> Keep B8
    'B7',         # Drop RedEdge-3 (r = 0.9929 with NIR B8) -> Keep B8
    'B8A',        # Drop Narrow NIR (r = 0.9936 with NIR B8) -> Keep B8
    'B12',        # Drop SWIR-2 (r = 0.9646 with SWIR-1 B11) -> Keep B11
    'EVI',        # Drop EVI (r = 0.9670 with NDVI) -> Keep NDVI
    'SAVI',       # Drop SAVI (r = 0.9735 with NDVI) -> Keep NDVI
    'NDWI',       # Drop NDWI (r = -0.9520 with NDVI) -> Keep MNDWI (better for urban areas)
    'GLCM_ASM'    # Drop GLCM_ASM (r = -0.9708 with GLCM_Entropy) -> Keep GLCM_Entropy
]


def load_and_preprocess_dataset(
    csv_path: str,
    test_size: float = 0.20,
    random_state: int = 42,
    prune_multicollinear: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str]]:
    """
    Loads GAMA multi-sensor dataset, handles label indexing, prunes collinear features,
    and returns stratified train/test partitions.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Training dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Determine target column
    target_col = None
    for cand in ['LULC_CLASS', 'class', 'label']:
        if cand in df.columns:
            target_col = cand
            break
    if target_col is None:
        raise ValueError(f"Target column not found in columns: {df.columns.tolist()}")

    # Prune collinear features
    if prune_multicollinear:
        to_drop = [c for c in COLS_TO_DROP if c in df.columns]
        df_clean = df.drop(columns=to_drop)
    else:
        df_clean = df.copy()

    X = df_clean.drop(columns=[target_col])
    # 0-index labels: 1..4 -> 0..3
    y_raw = df_clean[target_col].astype(int)
    if y_raw.min() == 1:
        y = y_raw - 1
    else:
        y = y_raw

    feature_names = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    return X_train, X_test, y_train, y_test, feature_names
