"""
Coastal Geomorphic Dynamics & Digital Shoreline Analysis System (DSAS)
Author: Emmanuel Yerbo
BSc Geography and Regional Planning, University of Cape Coast, Ghana
"""

import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_dsas_metrics(stats_shp_path):
    """
    Load DSAS transect rate-of-change statistics and compute
    summary geomorphic indices:
    - Net Shoreline Movement (NSM): Distance between oldest and youngest shoreline (m)
    - End Point Rate (EPR): Net change divided by elapsed time (m/yr)
    - Linear Regression Rate (LRR): Fitting all historical shorelines
    """
    print(f"[*] Loading transect statistics from: {stats_shp_path}")
    gdf = gpd.read_file(stats_shp_path)
    
    print(f"[+] Loaded {len(gdf)} coastal transects.")
    print("[*] Available columns:", list(gdf.columns))
    
    # Identify numeric rate columns
    numeric_cols = gdf.select_dtypes(include=[np.number]).columns.tolist()
    print("[*] Numerical metrics identified:", numeric_cols)
    
    summary = gdf[numeric_cols].describe().T
    print("\n=== COASTAL GEOMORPHIC RATE SUMMARY ===")
    print(summary[['mean', 'std', 'min', '50%', 'max']])
    
    return gdf, summary

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shp_file = os.path.join(base_dir, "data", "CHANTE_STATS.shp")
    if os.path.exists(shp_file):
        compute_dsas_metrics(shp_file)
    else:
        print(f"[!] Shapefile not found at {shp_file}")
