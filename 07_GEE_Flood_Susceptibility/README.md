# 🌊 Cloud-Based Multi-Criteria Flood Susceptibility Modeling in Google Earth Engine

> ### ⚡ Executive Summary (3 Sentences)
> 1. **Core Problem:** Seasonal monsoon downpours and spillage events across the Lower Volta Basin repeatedly displace riverine communities, yet local authorities lack real-time cloud-native tools to forecast regional flood vulnerability.
> 2. **Technical Pipeline:** We developed an automated multi-criteria weighted overlay pipeline in the Google Earth Engine JavaScript API, fusing SRTM 30m DEM elevation, slope gradients, MERIT Hydro Height Above Nearest Drainage (HAND), JRC 24-year surface water recurrence, and ESA WorldCover 10m land cover.
> 3. **Quantified Impact:** The system delineated 37.5% of the lower basin as high-to-severe flood risk zones, closely mirroring historical disaster records from Ghana's National Disaster Management Organisation (NADMO) and providing spatial zoning evidence for municipal evacuation routes.

### 📊 Empirical Performance & Validation Evidence
```text
====================== MULTI-CRITERIA DECISION MATRIX (AHP WEIGHTS) ======================
Spatial Parameter                   | Data Source & Resolution  | Criterion Weight | Rationale
------------------------------------+---------------------------+------------------+------------------------------
Height Above Nearest Drainage (HAND)| MERIT Hydro (90m)         | 30%              | Primary hydraulic flood head
Elevation & Slope Gradients         | SRTM 1 Arc-Second (30m)   | 25%              | Gravity-driven runoff ponding
Historical Flood Recurrence (2000-24)| JRC Global Surface Water  | 20%              | Historical inundation proof
Land Use / Impervious Cover         | ESA WorldCover (10m)      | 15%              | Surface infiltration capacity
Proximity to Major Drainage Channels| HydroSHEDS River Network  | 10%              | Riverine overflow buffering
------------------------------------+---------------------------+------------------+------------------------------
ZONATION OUTPUT: Very High Risk: 14.2% | High Risk: 23.3% | Moderate: 31.5% | Low: 31.0%
===========================================================================================
```

---


[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-JavaScript%20API-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![Volta Region](https://img.shields.io/badge/Domain-Volta%20Region%2C%20Ghana-blue)](https://earthengine.google.com/)

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