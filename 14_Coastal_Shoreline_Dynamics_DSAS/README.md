# 🌊 Coastal Geomorphic Dynamics: Shoreline Migration & DSAS Erosion Modeling

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14-green?logo=python&logoColor=white)](https://geopandas.org/)
[![DSAS](https://img.shields.io/badge/USGS-DSAS%20v5.0-006699)](https://www.usgs.gov/centers/whcmsc/science/digital-shoreline-analysis-system-dsas)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Author:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours) — University of Cape Coast, Ghana*  
> 🔗 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

West Africa's Gulf of Guinea coastline experiences some of the highest coastal recession rates in the world due to sea-level rise, intensified swell energy, and human interventions (e.g., dam-induced sediment starvation, beach sand mining). 

This research project conducts a multi-decadal spatiotemporal investigation of coastal migration dynamics along vulnerable coastal stretches in Ghana using the **Digital Shoreline Analysis System (DSAS)** and **GeoPandas**. By casting orthogonal transects across historical shorelines (1986–2024), we calculate geomorphic indices—**Net Shoreline Movement (NSM)**, **End Point Rate (EPR)**, and **Linear Regression Rate (LRR)**—to identify critical erosion hotspots and accretion regimes.

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

## 📊 Published Figures & Spatial Empirical Outputs

All analytical outputs are generated and verified in `results/`:

| Figure | Description | Focus Metric |
|---|---|---|
| **`fig1_erosion_accretion_map.png`** | Spatial transect zonation map across the study reach | Coastal segment categorization |
| **`fig2_temporal_shoreline_migration.png`** | Multi-epoch shoreline overlay (1986–2024) | High-water line (HWL) dynamics |
| **`fig3_nsm_hotspot_map.png`** | Net Shoreline Movement (NSM) hot-spot spatial clustering | Extreme recession zones ($> -3.5\text{ m/yr}$) |
| **`fig4_rate_histogram.png`** | Probability distribution of annual erosion rates | Skewness of sediment transport |
| **`fig5_decadal_comparison.png`** | Decadal epoch rate comparisons (1990s vs 2000s vs 2020s) | Acceleration of retreat |
| **`fig6_timeseries_top_eroding.png`** | Time-series trajectory of top critical transects | Infrastructure vulnerability |

---

## 📂 Project Structure

```text
14_Coastal_Shoreline_Dynamics_DSAS/
├── README.md                      <-- Comprehensive scientific report (You are here)
├── requirements.txt               <-- Python dependencies
├── data/
│   ├── CHANTE_STATS.shp           <-- Transect rate-of-change shapefile with EPR & NSM
│   └── SHORE.shp                  <-- Multi-epoch vectorized historical shorelines
├── results/                       <-- 8 high-resolution publication maps & figures
│   ├── fig1_erosion_accretion_map.png
│   ├── fig2_temporal_shoreline_migration.png
│   ├── fig3_nsm_hotspot_map.png
│   ├── fig4_rate_histogram.png
│   ├── fig5_decadal_comparison.png
│   └── fig6_timeseries_top_eroding.png
└── src/
    └── dsas_shoreline_analysis.py <-- Automated geomorphic metrics extraction
```

---

## ⚡ Quickstart

```bash
cd 14_Coastal_Shoreline_Dynamics_DSAS
pip install -r requirements.txt
python src/dsas_shoreline_analysis.py
```
