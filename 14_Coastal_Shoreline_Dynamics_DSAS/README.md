# 🌊 Coastal Geomorphic Dynamics: Shoreline Migration & DSAS Erosion Modeling
## Multi-Decadal Spatiotemporal Investigation of the Gulf of Guinea Coastline

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14-green?logo=python&logoColor=white)](https://geopandas.org/)
[![DSAS](https://img.shields.io/badge/USGS-DSAS%20v5.0-006699)](https://www.usgs.gov/centers/whcmsc/science/digital-shoreline-analysis-system-dsas)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

1. **The Core Coastal Problem:** West Africa's Gulf of Guinea coastline experiences some of the most critical coastal recession rates globally due to sea-level rise, intensified swell energy, and human interventions (e.g., dam-induced sediment starvation, beach sand mining).
2. **The Technical Pipeline:** This research conducts a multi-decadal spatiotemporal investigation of coastal migration dynamics along vulnerable coastal stretches in Ghana using the **Digital Shoreline Analysis System (DSAS)** and **GeoPandas**. By casting orthogonal transects across historical shorelines (1986–2024), we calculate geomorphic indices—**Net Shoreline Movement (NSM)**, **End Point Rate (EPR)**, and **Linear Regression Rate (LRR)**.
3. **Quantified Impact:** The pipeline identified critical erosion hot-spots experiencing annual retreat velocities exceeding **$-3.5\text{ m/year}$**, providing empirical engineering baselines for national sea defense projects and coastal zone management.

---

## 🔬 Architectural Workflow & Geomorphic Modeling

```mermaid
flowchart TD
    subgraph INP["1. Multi-Temporal Earth Observation Ingestion (1986–2024)"]
        A["🛰️ Multi-Decadal Landsat 5, 7, 8 & Sentinel-2 Archives"] --> B["🏖️ High-Water Line (HWL) Proxy Extraction<br/>(MNDWI / AWEI Water Index Thresholding & Sub-Pixel Snapping)"]
    end

    subgraph DSAS["2. Orthogonal Geomorphic Transect Casting"]
        B --> C["📏 Baseline Generation (Offshore / Onshore Reference Curve)"]
        C --> D["📐 Cast Orthogonal Transects at 50m Regular Spacing<br/>(Intersection point coordinate extraction across epochs)"]
    end

    subgraph METRICS["3. Statistical Rate Formulations"]
        D --> E1["NSM: Net Shoreline Movement (D_new - D_old)"]
        D --> E2["EPR: End Point Rate (NSM / Δt [m/yr])"]
        D --> E3["LRR: Linear Regression Rate (Least Squares Multi-Epoch)"]
    end

    subgraph OUT["4. Coastal Vulnerability & Risk Zonation"]
        E1 & E2 & E3 --> F["🔥 Erosion Hotspot Clustering (> -3.5 m/yr Recession)"]
        F --> G["🏛️ Coastal Protection & Sea Defense Engineering Evidence"]
    end

    style INP fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style DSAS fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc
    style METRICS fill:#022c22,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style OUT fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc
```

---

## 🖼️ Visual Empirical Evidence & Published Figures

### 1. Spatial Shoreline Migration & Transect Zonation
<p align="center">
  <img src="results/fig1_erosion_accretion_map.png" width="49%" alt="Erosion and Accretion Spatial Zonation Map">
  <img src="results/fig2_temporal_shoreline_migration.png" width="49%" alt="Multi-Epoch Shoreline Migration (1986-2024)">
</p>

> **Left**: Comprehensive spatial transect zonation categorizing the coastal reach into severe erosion, moderate recession, stable, and accretion regimes.  
> **Right**: Multi-decadal historical shoreline vector positions (1986–2024) capturing long-term landward translation of the High Water Line.

---

### 2. Hotspot Spatial Clustering & Rate Probability Distributions
<p align="center">
  <img src="results/fig3_nsm_hotspot_map.png" width="49%" alt="Net Shoreline Movement Hotspot Spatial Clustering">
  <img src="results/fig4_rate_histogram.png" width="49%" alt="Probability Distribution of Annual Shoreline Change Rates">
</p>

> **Left**: Net Shoreline Movement (NSM) hotspot clustering isolating the spatial focal points of catastrophic retreat.  
> **Right**: Frequency distribution histogram of calculated annual migration rates, demonstrating negative skewness dominated by coastal sediment deficit.

---

### 3. Decadal Trajectories & High-Vulnerability Transects
<p align="center">
  <img src="results/fig5_decadal_comparison.png" width="49%" alt="Decadal Shoreline Change Rate Comparison">
  <img src="results/fig6_timeseries_top_eroding.png" width="49%" alt="Time Series Trajectory of Top Critical Eroding Transects">
</p>

> **Left**: Epochal comparison across the 1990s, 2000s, 2010s, and 2020s proving non-linear acceleration of coastal erosion.  
> **Right**: Longitudinal displacement curves for the most severely threatened transect points adjacent to critical settlement infrastructure.

---

## 🔬 Geomorphic Rate Formulations

### 1. Net Shoreline Movement (NSM)
Measures the absolute physical distance between the oldest ($t_{\text{old}}$) and most recent ($t_{\text{new}}$) extracted shoreline:
$$\text{NSM} = D_{\text{new}} - D_{\text{old}} \quad [\text{meters}]$$
* Negative values indicate net landward recession (erosion); positive values indicate seaward progradation (accretion).

### 2. End Point Rate (EPR)
Quantifies the annual velocity of shoreline migration:
$$\text{EPR} = \frac{\text{NSM}}{t_{\text{new}} - t_{\text{old}}} \quad [\text{m/year}]$$

### 3. Linear Regression Rate (LRR)
Fits a least-squares linear trend through all intermediate multi-epoch shoreline intercepts, minimizing episodic storm surge anomalies:
$$y = mx + b \implies \text{LRR} = m \quad [\text{m/year}]$$

---

## 📂 Project Structure

```text
14_Coastal_Shoreline_Dynamics_DSAS/
├── README.md                      <-- Comprehensive scientific report (You are here)
├── requirements.txt               <-- Python dependencies (geopandas, shapely, scipy, matplotlib)
├── rate_of_change.py              <-- Modular shoreline extraction & DSAS calculation engine
├── results/                       <-- Verified empirical publication figures
│   ├── fig1_erosion_accretion_map.png
│   ├── fig2_temporal_shoreline_migration.png
│   ├── fig3_nsm_hotspot_map.png
│   ├── fig4_rate_histogram.png
│   ├── fig5_decadal_comparison.png
│   └── fig6_timeseries_top_eroding.png
└── shapefiles/                    <-- Spatial GIS layers (shorelines, baseline, transects)
```

---

## ⚡ Quickstart

```bash
# Navigate to project folder
cd 14_Coastal_Shoreline_Dynamics_DSAS

# Install dependencies
pip install -r requirements.txt

# Execute shoreline analysis
python rate_of_change.py
```
