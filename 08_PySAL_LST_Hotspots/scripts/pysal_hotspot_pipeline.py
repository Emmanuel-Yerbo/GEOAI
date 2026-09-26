"""
Spatial Autocorrelation and LST Hotspot Modeling with PySAL
Author: Emmanuel Yerbo
"""
import numpy as np
import rasterio
import geopandas as gpd
from libpysal.weights import DistanceBand
from esda.moran import Moran, Moran_Local

def compute_getis_ord_gistar(gdf, value_col="lst_celsius", threshold_dist=1500.0):
    """
    Computes Getis-Ord Gi* z-scores to isolate statistically significant thermal hotspots.
    """
    # Create projected spatial weight matrix
    w = DistanceBand.from_dataframe(gdf, threshold=threshold_dist, binary=True)
    w.transform = 'B'
    
    y = gdf[value_col].values
    n = len(y)
    y_mean = np.mean(y)
    s = np.std(y)
    
    gi_z = []
    for i in range(n):
        neighbors = w.neighbors[i]
        sum_wij = len(neighbors)
        sum_wij_yj = np.sum(y[neighbors])
        numerator = sum_wij_yj - (y_mean * sum_wij)
        denom = s * np.sqrt(((n * sum_wij) - (sum_wij ** 2)) / (n - 1))
        z = numerator / (denom + 1e-12)
        gi_z.append(z)
        
    gdf["gi_star_zscore"] = gi_z
    gdf["is_hotspot_99"] = gdf["gi_star_zscore"] > 2.58  # p < 0.01
    return gdf
