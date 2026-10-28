# 🌊 Cloud-Based Multi-Criteria Flood Susceptibility Modeling in Google Earth Engine
## Case Study: Lower Volta Basin Regional Flood Hazard Zonation (Volta Region, Ghana)

[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-JavaScript%20API-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![Volta Region](https://img.shields.io/badge/Domain-Volta%20Region%2C%20Ghana-blue)](https://earthengine.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

### ⚡ Executive Summary

1. **The Core Spatial Problem:** Seasonal monsoon downpours and spillage events across the Lower Volta Basin repeatedly displace riverine communities, yet local authorities lack real-time cloud-native tools to forecast regional flood vulnerability.
2. **The Technical Pipeline:** We developed an automated multi-criteria weighted overlay pipeline in the Google Earth Engine JavaScript API, fusing SRTM 30m DEM elevation, slope gradients, MERIT Hydro Height Above Nearest Drainage (HAND), JRC 24-year surface water recurrence, and ESA WorldCover 10m land cover.
3. **Quantified Impact:** The system delineated **37.5% of the lower basin as high-to-severe flood risk zones**, closely mirroring historical disaster records from Ghana's National Disaster Management Organisation (NADMO) and providing spatial zoning evidence for municipal evacuation routes.

### 📊 Empirical Performance & Validation Evidence

| Spatial Parameter | Data Source & Resolution | Criterion Weight | Hydro-Geomorphic Rationale |
|---|---|:---:|---|
| **Height Above Nearest Drainage (HAND)** | MERIT Hydro (90m) | **30%** | Primary hydraulic head above drainage |
| **Elevation & Slope Gradients** | SRTM 1 Arc-Second (30m) | **25%** | Gravity-driven runoff ponding in depressions |
| **Historical Flood Recurrence (2000–24)** | JRC Global Surface Water | **20%** | Empirical proof of chronic inundation |
| **Land Use / Impervious Cover** | ESA WorldCover (10m) | **15%** | Infiltration capacity vs. runoff acceleration |
| **Proximity to Major River Channels** | HydroSHEDS Drainage Network | **10%** | Fluvial overflow buffer vulnerability |

#### Basin Hazard Zonation Distribution
- **Very High / Severe Risk:** **14.2%** *(Keta, Anloga, Mepe, Battor floodplains)*
- **High Risk:** **23.3%** *(Riparian agricultural margins)*
- **Moderate Risk:** **31.5%**
- **Low / Minimal Risk:** **31.0%** *(Inland bedrock uplands)*

---

### 🔬 Methodological Flow & Multi-Criteria Overlay

```mermaid
flowchart TD
    subgraph DATA["1. Cloud-Native Earth Observation Ingestion (GEE)"]
        D1["SRTM 30m DEM & Slope Gradients"]
        D2["MERIT Hydro 90m (HAND Index)"]
        D3["JRC Global Surface Water (2000–2024 Recurrence)"]
        D4["ESA WorldCover 10m (Impervious Surfaces)"]
        D5["HydroSHEDS River Channels (Euclidean Proximity)"]
    end

    subgraph AHP["2. Multi-Criteria AHP Weighting & Normalization"]
        D1 -->|"25% Weight"| W["Analytical Hierarchy Process (AHP)<br/>Consistency Ratio CR < 0.05"]
        D2 -->|"30% Weight (Primary Head)"| W
        D3 -->|"20% Weight (History)"| W
        D4 -->|"15% Weight (Infiltration)"| W
        D5 -->|"10% Weight (Distance)"| W
    end

    subgraph OUT["3. Spatial Zonation & Disaster Response"]
        W --> Z["🌊 Composite Flood Susceptibility Index (FSI)<br/>FSI = Σ (w_i · C_i)"]
        Z --> Z1["Severe / Very High Risk: 14.2% (Keta / Anloga / Mepe)"]
        Z --> Z2["High Risk: 23.3% (Lower Volta Basin Floodplains)"]
        Z --> Z3["Moderate & Low Risk: 62.5% (Inland Highlands)"]
        Z1 & Z2 --> NADMO["🏛️ NADMO Disaster Management & Evacuation Routing"]
    end

    style DATA fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style AHP fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc
    style OUT fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc
```

## 📌 Overview
A cloud-native multi-criteria weighted overlay framework engineered in **Google Earth Engine (GEE JavaScript API)** to map regional flood susceptibility across the lower Volta Basin.

![Multi-Criteria Flood Mapping](results/multicriteria_flood_mapping.jpg)

### Data Synthesis:
- **Terrain:** SRTM 30m Digital Elevation Model & derived slope gradients.
- **Hydrology:** MERIT Hydro Height Above Nearest Drainage (HAND).
- **Surface Water Dynamics:** JRC Global Surface Water 24-year recurrence history (2000–2024).
- **Land Cover:** ESA WorldCover 10m global land cover product.

### Hazard Zonation Findings:
- Classified **37.5% of the Volta Region** under high-to-extreme flood susceptibility.
- Validated spatial hazard patterns against historical disaster records from Ghana's **National Disaster Management Organisation (NADMO)** for Keta, Anloga, and Sogakofe.