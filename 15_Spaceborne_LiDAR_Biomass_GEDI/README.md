# 🌲 Spaceborne LiDAR & Optical Fusion: Forest Biomass Density (NASA GEDI + Sentinel-2)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![NASA GEDI](https://img.shields.io/badge/NASA-GEDI%20L4A%20LiDAR-blue)](https://gedi.umd.edu/)
[![Sentinel-2](https://img.shields.io/badge/ESA-Sentinel--2%20MSI-003399)](https://sentinels.copernicus.eu/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Random%20Forest%20%2F%20GBDT-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

Accurate estimation of **Aboveground Biomass Density (AGBD)** and terrestrial carbon stocks is essential for REDD+ monitoring, climate mitigation policies, and biodiversity conservation. However, optical satellite sensors (e.g., Landsat, Sentinel-2) suffer from severe **spectral saturation** over dense tropical canopies, while airborne LiDAR campaigns are prohibitively expensive over continental scales.

This research project develops a multi-sensor fusion pipeline coupling spaceborne full-waveform LiDAR from the **NASA GEDI mission (Global Ecosystem Dynamics Investigation, L4A Footprint Level)** with multi-spectral reflectance tensors from **ESA Sentinel-2 MSI** across the **Kakum National Forest** in Ghana. Machine learning regressors (Random Forest and Gradient Boosted Trees) extrapolate discrete LiDAR canopy height metrics ($RH_{50}, RH_{98}$) into spatially contiguous, wall-to-wall 10m biomass maps.

---

## 🔬 Multi-Sensor Fusion Framework & Architecture

```mermaid
flowchart TD
    subgraph INP["1. Multi-Sensor Spaceborne Data Ingestion"]
        G["🛰️ NASA GEDI Spaceborne LiDAR (ISS L4A)<br/>Waveform Metrics: RH50, RH98, Canopy Cover, PAI"]
        S["🛰️ ESA Sentinel-2 MSI (10m L2A)<br/>B2–B8A, Red-Edge, NDRE, EVI, NDVI"]
    end

    subgraph FUSE["2. Spatial Co-Registration & Feature Engineering"]
        G & S --> C["📐 25m Footprint Spatial Extraction & Buffer Alignment<br/>(Combines 3D vertical structure with 2D horizontal texture)"]
    end

    subgraph ML["3. Supervised Non-Linear Regressors"]
        C --> M1["🌲 Spatial Random Forest Regressor (R² = 0.84)"]
        C --> M2["⚡ Gradient Boosted Decision Trees (GBDT)"]
    end

    subgraph OUT["4. Wall-to-Wall Carbon Stock Accounting"]
        M1 & M2 --> W["🗺️ 10m Spatially Continuous AGBD Map [Mg/ha]<br/>(Resolves optical saturation over Kakum National Forest)"]
        W --> R["📊 REDD+ National Carbon Verification & MRV Compliance"]
    end

    style INP fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style FUSE fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc
    style ML fill:#022c22,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style OUT fill:#064e3b,stroke:#22c55e,stroke-width:2px,color:#f8fafc
```

### 1. Biophysical LiDAR Metrics (GEDI L4A)
- **$RH_{98}$ (Canopy Height):** Relative height metric at 98% returned energy, representing maximum top-of-canopy height.
- **$RH_{50}$ (Canopy Median Height):** 50% energy return, capturing vertical canopy density and understory structure.
- **Canopy Cover:** Percentage of ground obscured by vegetation at beam incidence.

### 2. Multi-Spectral Optical Covariates (Sentinel-2)
- **Normalized Difference Red Edge (NDRE):** Mitigates saturation over high biomass tropical canopies:
  $$\text{NDRE} = \frac{B_8 - B_5}{B_8 + B_5}$$
- **Enhanced Vegetation Index (EVI):** Decoupled canopy background reflectance and atmospheric resistance:
  $$\text{EVI} = 2.5 \times \frac{\text{NIR} - \text{Red}}{\text{NIR} + 6.0 \cdot \text{Red} - 7.5 \cdot \text{Blue} + 1}$$

---

## 📊 Empirical Findings & Carbon Stocks

- **Peak Biomass Core (~585.84 Mg/ha):** Concentrated in pristine, mature evergreen primary forest compartments with emergent trees exceeding 45m.
- **Ecosystem Regrowth Zones (~19.25–120.0 Mg/ha):** Located along forest reserve boundaries and transition zones undergoing secondary succession.
- **Cross-Validation Accuracy:** Achieved $R^2 = 0.84$ ($RMSE = 28.4\text{ Mg/ha}$), significantly outperforming purely optical models ($R^2 = 0.58$).

---

## 📂 Project Structure

```text
15_Spaceborne_LiDAR_Biomass_GEDI/
├── README.md                               <-- Comprehensive scientific report (You are here)
├── requirements.txt                        <-- Python dependencies
└── src/
    └── gedi_sentinel_biomass_regressor.py  <-- Full ML fusion & regression pipeline
```

---

## ⚡ Quickstart

```bash
cd 15_Spaceborne_LiDAR_Biomass_GEDI
pip install -r requirements.txt
python src/gedi_sentinel_biomass_regressor.py
```
