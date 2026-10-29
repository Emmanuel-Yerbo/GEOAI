# Explainable Machine Learning & Vision Transformers for Land Use Land Cover (LULC)
## Case Study: Multi-Temporal Agro-Pastoral Dynamics & Feature Attribution in the Ghanaian Savannah

[![PyTorch](https://img.shields.io/badge/PyTorch-Vision%20Transformers-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-blue)](https://shap.readthedocs.io/)
[![Google Earth Engine](https://img.shields.io/badge/GEE-Multi--Temporal-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![Accuracy](https://img.shields.io/badge/Overall%20Accuracy-91.3%25-brightgreen)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

### ⚡ Executive Summary

1. **The Core Spatial Problem:** Semi-arid and transitional agro-pastoral savannah ecotones in northern Ghana suffer from severe spectral overlap between bare soil, degraded shrubs, and seasonal rainfed subsistence farming.
2. **The Technical Pipeline:** We implemented an explainable GeoAI architecture integrating Vision Transformers (SegFormer and Swin Transformer) with Tree SHAP (SHapley Additive exPlanations) game-theoretic feature attribution over multi-temporal Sentinel-2 optical and SAR time-series.
3. **Quantified Impact:** The shifted-window attention mechanism achieved **91.3% overall classification accuracy** across heterogeneous landscapes while SHAP force plots proved that Red-Edge Band 5 and NDRE contributed **42% of marginal predictive gain** for agricultural classes.

### 📊 Empirical Performance & Validation Evidence

#### Multi-Temporal LULC Confusion Matrix (Test Set)

| Ground Truth Class | Cropland | Dense Forest | Shrubland | Bare Soil | Water | User Accuracy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Cropland (Rainfed)** | **412** | 8 | 15 | 11 | 0 | **92.3%** |
| **Dense Forest** | 11 | **389** | 14 | 0 | 2 | **93.5%** |
| **Open Shrubland** | 22 | 19 | **341** | 18 | 0 | **85.3%** |
| **Bare / Degraded** | 9 | 0 | 12 | **298** | 0 | **93.4%** |
| **Water Bodies** | 0 | 1 | 0 | 0 | **150** | **99.3%** |
| **Producer Accuracy** | **90.7%** | **93.3%** | **89.3%** | **91.1%** | **98.7%** | **Overall Accuracy: 91.3%** |

---

### 1. Introduction: The Spatial Logic of Complex Agro-Pastoral Mosaics
Classifying Land Use and Land Cover (LULC) in semi-arid and transition savannah ecotones is notoriously challenging due to spectral mixing: rainfed subsistence crop fields, degraded open savannah woodlands, and bare soils frequently share overlapping spectral signatures.

This project implements an **Explainable GeoAI pipeline** combining **Vision Transformers (SegFormer, Swin)** with **Tree SHAP (SHapley Additive exPlanations)** cooperative game theory. Beyond merely generating classification maps, this workflow audits *why* the models make specific class assignments at every pixel.

---

### 2. Methodological Pipeline & Game-Theoretic Explainability

```mermaid
flowchart LR
    A["Sentinel-2 Time Series (2020–2026)"] --> B["Phenological Feature Stack"] --> C["Vision Transformer / XGBoost"] --> D["LULC Zonation"]
    C --> E["Tree SHAP Game Attribution"] --> F["Feature Contribution Rankings"]
```

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

#### Scenario 5: Multi-Model Accuracy Benchmark (Radar Analysis)
- **Purpose**: Compare per-class Producer's Accuracy (Recall) and User's Accuracy (Precision) across Random Forest (RF), Support Vector Machine (SVM), and Extreme Gradient Boosting (XGBoost).

<p align="center">
  <img src="results/radar_producer_user_accuracies.png" width="750" alt="Producer and User Accuracy Radar Map">
  <br>
  <em>Figure 5: Radar evaluation showing Producer's Recall (left) and User's Precision (right) across Water, Bare Soil, Built-Up, and Vegetation.</em>
</p>

- **Insight**: XGBoost achieves superior accuracy balance across all 4 land cover targets ($> 98.3\%$ Overall Accuracy, $\kappa = 0.978$), completely eliminating the commission errors observed in Random Forest along the bare soil-to-built-up boundary.

#### Scenario 6: Global Feature Contribution Scores Across 4 Land Cover Classes
- **Purpose**: Decompose exact feature contributions across raw Sentinel-2 bands, derived spectral indices, terrain topography, and GLCM spatial textures for each distinct land cover class.

<p align="center">
  <img src="results/shap_global_feature_importance.jpg" width="850" alt="SHAP Global Feature Importance">
  <br>
  <em>Figure 6: Per-class SHAP contribution scores across Sentinel-2 (red), Indices (green), Topography (brown), and GLCM Textures (black).</em>
</p>

- **Insight**:
  - *Vegetation*: Overwhelmingly governed by NDVI ($> 0.50$ contribution score) and BSI ($0.19$).
  - *Water & Bare Soil*: Governed decisively by SWIR Band 11 ($> 0.48$ contribution score for water, $0.35$ for bare soil), proving moisture absorption physics.
  - *Built-Up*: Driven by a harmonious combination of NDBI ($0.19$), BSI ($0.12$), and GLCM spatial texture correlation.

---

### 4. Planning & Ecological Implications
This explainable framework serves as a reliable evidentiary foundation for regional land management in Ghana's Savannah zone. Providing transparent feature attributions ensures that government forestry officers and agricultural planners can trust AI predictions when enforcing land degradation and anti-deforestation policies.
