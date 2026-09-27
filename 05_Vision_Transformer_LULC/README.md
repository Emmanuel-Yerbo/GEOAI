# Explainable Machine Learning & Vision Transformers for Land Use Land Cover (LULC)
## Case Study: Multi-Temporal Agro-Pastoral Dynamics & Feature Attribution in the Ghanaian Savannah

[![PyTorch](https://img.shields.io/badge/PyTorch-Vision%20Transformers-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-blue)](https://shap.readthedocs.io/)
[![Google Earth Engine](https://img.shields.io/badge/GEE-Multi--Temporal-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)

### 1. Introduction: The Spatial Logic of Complex Agro-Pastoral Mosaics
Classifying Land Use and Land Cover (LULC) in semi-arid and transition savannah ecotones is notoriously challenging due to spectral mixing: rainfed subsistence crop fields, degraded open savannah woodlands, and bare soils frequently share overlapping spectral signatures.

This project implements an **Explainable GeoAI pipeline** combining **Vision Transformers (SegFormer, Swin)** with **Tree SHAP (SHapley Additive exPlanations)** cooperative game theory. Beyond merely generating classification maps, this workflow audits *why* the models make specific class assignments at every pixel.

---

### 2. Methodological Pipeline

#### 2.1 Multi-Temporal Earth Observation Harmonization
- **The Process**: Multi-spectral imagery from Sentinel-2 MSI and Landsat is atmospherically corrected and harmonized into multi-temporal composites spanning 2020 to 2026.
- **The Essence**: Temporal stacks allow models to observe the **phenological trajectory** of vegetation (greening vs senescence), resolving spectrally ambiguous classes that look identical in single-date snapshots.

#### 2.2 Cooperative Game Theory Attribution (Tree SHAP)
- **The Process**: For each pixel classification, Shapley values are calculated across all spectral bands and index derivatives to quantify exact marginal contributions.
- **The Essence**: Guarantees local accuracy and consistency. Unmasks potential shortcut learning (e.g. models relying on spurious topographic artifacts rather than true vegetative reflectance).

---

### 3. Scenario Analysis: Spatial & Biophysical Insights

#### Scenario 1: Multi-Temporal Savannah Transitions
- **Purpose**: Delineating agricultural expansion versus woodland loss across multi-year intervals.

<p align="center">
  <img src="results/lulc_classification_map.png" width="450" alt="LULC Baseline">
  <img src="results/lulc_2022_map.png" width="450" alt="LULC 2022 Monitoring">
  <br>
  <em>Figure 1: Baseline LULC spatial zonation (left) versus 2022 multi-temporal transition monitoring (right).</em>
</p>

- **Insight**: Highlights rapid **cropland fragmentation**. Subsistence agricultural encroachment penetrates deep into formerly protected savannah reserves, driving a net reduction in contiguous canopy cover.

#### Scenario 2: Global Biophysical Feature Importance
- **Purpose**: Ranking the most influential spectral bands and indices across the entire model decision tree.

<p align="center">
  <img src="results/feature_importance.png" width="550" alt="Global Feature Importance">
  <br>
  <em>Figure 2: Global feature importance showing dominance of Red Edge and Shortwave Infrared (SWIR) bands.</em>
</p>

- **Insight**: Demonstrates that Shortwave Infrared (SWIR1/SWIR2) and Red Edge (RE2/RE3) bands contribute over **62% of total predictive power**, outranking conventional NIR and NDVI by effectively discriminating moisture-stressed crop canopies from senescent savannah grasses.

#### Scenario 3: Local SHAP Force Attribution
- **Purpose**: Pixel-level explanation of classification push-and-pull factors.

<p align="center">
  <img src="results/shap_force_plot.png" width="850" alt="SHAP Force Plot">
  <br>
  <em>Figure 3: SHAP force plot demonstrating individual feature contributions toward a specific land cover assignment.</em>
</p>

- **Insight**: Provides transparent auditability for environmental monitoring. The force plot shows how elevated SWIR reflectance pushes predictions toward *Built-up/Bare Soil*, while high moisture index (NDMI) counters toward *Wetland/Vegetation*.

#### Scenario 4: Class-Specific Marginal Profiles
- **Purpose**: Auditing spectral response curves for distinct land cover targets.

<p align="center">
  <img src="results/builtup_profile.png" width="280" alt="Built-up Profile">
  <img src="results/bare_soil_profile.png" width="280" alt="Bare Soil Profile">
  <img src="results/water_profile.png" width="280" alt="Water Profile">
  <br>
  <em>Figure 4: Distinct marginal feature response curves for Built-up, Bare Soil, and Surface Water.</em>
</p>

- **Insight**: Confirms that the classifier adheres to established radiative transfer physics across all three critical non-vegetated classes without overfitting to noise.

---

### 4. Planning & Ecological Implications
This explainable framework serves as a reliable evidentiary foundation for regional land management in Ghana's Savannah zone. Providing transparent feature attributions ensures that government forestry officers and agricultural planners can trust AI predictions when enforcing land degradation and anti-deforestation policies.
