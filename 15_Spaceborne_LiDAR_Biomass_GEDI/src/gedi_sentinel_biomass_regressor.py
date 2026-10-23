"""
Spaceborne LiDAR & Optical Multi-Sensor Fusion for Aboveground Biomass Density (AGBD)
Author: Emmanuel Yerbo
BSc Geography and Regional Planning, University of Cape Coast, Ghana
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def generate_synthetic_gedi_sentinel_calibration(n_samples=1500, random_state=42):
    """
    Simulates GEDI L4A LiDAR waveform metrics and Sentinel-2 L2A optical reflectance
    tensors across tropical forest canopy (e.g. Kakum National Park, Ghana).
    """
    np.random.seed(random_state)
    
    # GEDI LiDAR canopy height metrics (meters)
    rh50 = np.random.uniform(5.0, 28.0, n_samples)
    rh98 = rh50 * np.random.uniform(1.2, 1.8, n_samples) + np.random.normal(0, 1.5, n_samples)
    canopy_cover = np.clip(rh98 / 35.0 + np.random.normal(0, 0.05, n_samples), 0.1, 0.98)
    
    # Sentinel-2 Multispectral indices
    ndvi = np.clip(0.4 + 0.5 * canopy_cover + np.random.normal(0, 0.03, n_samples), 0.1, 0.95)
    ndre = np.clip(0.2 + 0.6 * canopy_cover + np.random.normal(0, 0.04, n_samples), 0.05, 0.85)
    evi = 2.5 * ((ndvi - 0.2) / (ndvi + 2.4))
    
    # Non-linear allometric relationship for true AGBD (Mg/ha)
    # Power-law allometry: AGBD = a * (RH98)^b * (Cover)^c
    true_agbd = 0.85 * (rh98 ** 1.62) * (canopy_cover ** 0.8) + np.random.normal(0, 12.0, n_samples)
    true_agbd = np.clip(true_agbd, 15.0, 600.0)
    
    df = pd.DataFrame({
        'rh50': rh50,
        'rh98': rh98,
        'canopy_cover': canopy_cover,
        'ndvi': ndvi,
        'ndre': ndre,
        'evi': evi,
        'agbd_label_mgha': true_agbd
    })
    return df

def train_biomass_regressor(data_df):
    features = ['rh50', 'rh98', 'canopy_cover', 'ndvi', 'ndre', 'evi']
    X = data_df[features]
    y = data_df['agbd_label_mgha']
    
    print(f"[*] Training Multi-Sensor Biomass Fusion Regressor across {len(X)} samples...")
    rf = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    r2_scores = cross_val_score(rf, X, y, cv=kf, scoring='r2')
    rmse_scores = np.sqrt(-cross_val_score(rf, X, y, cv=kf, scoring='neg_mean_squared_error'))
    
    rf.fit(X, y)
    y_pred = rf.predict(X)
    
    print("\n=== MODEL PERFORMANCE METRICS ===")
    print(f"Mean 5-Fold R² Score:   {r2_scores.mean():.4f} (+/- {r2_scores.std():.4f})")
    print(f"Mean 5-Fold RMSE:       {rmse_scores.mean():.2f} Mg/ha")
    print(f"Overall MAE:            {mean_absolute_error(y, y_pred):.2f} Mg/ha")
    
    importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    print("\n=== FEATURE IMPORTANCE RANKING ===")
    for feat, imp in importances.items():
        print(f"  {feat:15s}: {imp*100:.2f}%")
        
    return rf, importances

if __name__ == "__main__":
    df = generate_synthetic_gedi_sentinel_calibration()
    model, imp = train_biomass_regressor(df)
