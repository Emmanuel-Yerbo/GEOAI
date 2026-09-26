import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

def create_geographic_blocks(df, lon_col="longitude", lat_col="latitude", block_size_deg=0.01):
    """
    Partitions spatial coordinates into discrete spatial grid blocks (~1.1 km at 0.01 deg).
    Prevents spatial autocorrelation data leakage between training and testing folds.
    """
    df = df.copy()
    df["block_x"] = np.floor(df[lon_col] / block_size_deg).astype(int)
    df["block_y"] = np.floor(df[lat_col] / block_size_deg).astype(int)
    df["spatial_block_id"] = df["block_x"].astype(str) + "_" + df["block_y"].astype(str)
    return df

def get_spatial_kfold_splits(df, n_splits=5, group_col="spatial_block_id"):
    """
    Returns train and test index splits grouped strictly by spatial block IDs.
    """
    gkf = GroupKFold(n_splits=n_splits)
    groups = df[group_col]
    X = df.drop(columns=[group_col])
    return list(gkf.split(X, groups=groups))
