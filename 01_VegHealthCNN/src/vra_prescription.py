"""
Crop-Agnostic Relative Nitrogen Demand Index (RNDI) and Variable-Rate Application (VRA) Engine
Reference: Yerbo (2026), Section 3.6, Equations 7 and 10.
"""
import numpy as np

def compute_rndi(crop_classes, ndre_array):
    """
    Computes the dimensionless Relative Nitrogen Demand Index (RNDI) across canopy pixels.
    
    Formula (Equation 7):
        RNDI(x, y) = 0.0,                                      if Y_hat = 2 (Non-Vegetation)
        RNDI(x, y) = clip(1.0 - NDRE(x, y), 0.05, 0.95),      if Y_hat in {0, 1} (Vegetated)
        
    Parameters:
    -----------
    crop_classes : np.ndarray
        Array of predicted classes (0: Healthy, 1: Moderate Stress, 2: Non-Vegetation).
    ndre_array : np.ndarray
        Normalized Difference Red Edge array (B7 - B5) / (B7 + B5).
        
    Returns:
    --------
    rndi : np.ndarray
        Continuous relative demand score in [0.0, 0.95].
    """
    rndi = np.zeros_like(ndre_array, dtype=np.float32)
    veg_mask = np.isin(crop_classes, [0, 1])
    
    # Inverted red-edge response: lower NDRE indicates higher relative nitrogen priority
    raw_demand = 1.0 - ndre_array[veg_mask]
    rndi[veg_mask] = np.clip(raw_demand, 0.05, 0.95)
    return rndi

def compute_vra_nitrogen(crop_classes, ndre_array, base_rate_kg_per_ha=120.0):
    """
    Computes parcel-scale Variable-Rate Nitrogen (VRN) application rates (Equation 10).
    
    Formula:
        VRA(x, y) = 0 kg N/ha,                                             if Y_hat = 2
        VRA(x, y) = clip(base_rate * (1.0 - NDRE(x, y)), 30, 180) kg N/ha, if Y_hat in {0, 1}
    """
    vra = np.zeros_like(ndre_array, dtype=np.float32)
    veg_mask = np.isin(crop_classes, [0, 1])
    
    prescribed = base_rate_kg_per_ha * (1.0 - ndre_array[veg_mask])
    vra[veg_mask] = np.clip(prescribed, 30.0, 180.0)
    return vra

if __name__ == "__main__":
    # Test sample with dummy inputs
    mock_classes = np.array([0, 1, 2, 0])
    mock_ndre = np.array([0.45, 0.22, 0.05, 0.52])
    
    rndi = compute_rndi(mock_classes, mock_ndre)
    vra = compute_vra_nitrogen(mock_classes, mock_ndre)
    
    for i in range(len(mock_classes)):
        cls_name = ["Healthy", "Moderate Stress", "Non-Veg"][mock_classes[i]]
        print(f"Sample {i+1} [{cls_name}]: NDRE={mock_ndre[i]:.2f} -> RNDI={rndi[i]:.3f}, VRA={vra[i]:.1f} kg N/ha")
