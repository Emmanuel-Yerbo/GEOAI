"""
Variable-Rate Application (VRA) Nitrogen Prescription Algorithm
Modulates nitrogen application based on NDRE-derived crop vigor zones.
"""
def compute_nitrogen_prescription(crop_health_classes, total_area_ha, uniform_rate_kg_per_ha=120.0):
    # Prescription mapping based on vigor:
    # Class 0 (Healthy): 70% of blanket rate (84 kg/ha)
    # Class 1 (Moderate Stress): 100% of blanket rate (120 kg/ha)
    # Class 2 (No-Vegetation/Galamsey): 0 kg/ha
    rates = {0: 84.0, 1: 120.0, 2: 0.0}
    
    total_uniform_n = total_area_ha * uniform_rate_kg_per_ha
    prescribed_n = sum(rates[c] * area for c, area in crop_health_classes.items())
    savings_kg = total_uniform_n - prescribed_n
    savings_pct = (savings_kg / total_uniform_n) * 100
    
    return {
        "blanket_rate_kg": total_uniform_n,
        "prescribed_rate_kg": prescribed_n,
        "savings_kg": savings_kg,
        "savings_pct": savings_pct
    }
