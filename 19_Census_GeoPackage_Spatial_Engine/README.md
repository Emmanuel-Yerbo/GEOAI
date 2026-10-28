# 🏛️ Spatial Demographic Database: OGC GeoPackage Engine & Multi-Decadal Census Harmonization

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![OGC GeoPackage](https://img.shields.io/badge/OGC-GeoPackage%201.3-blue)](https://www.geopackage.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14-green?logo=python&logoColor=white)](https://geopandas.org/)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

Real-world geospatial data science in developing nations faces severe data fragmentation, inconsistent administrative reporting, boundary changes over time, and incompatible formats (PDF census tables, loose CSVs, and disjoint shapefiles).

This project develops an open-source, reproducible **Spatial Demographic Database Engine** that harmonizes **multi-decadal census data (2010 vs. 2021 Ghana Population & Housing Census)** and reconciles the historical 10-region administrative framework with the modern 16-region administrative structure. The pipeline compiles these disparate datasets into a high-performance **OGC GeoPackage (`ghana_census_2021.gpkg`)** equipped with spatial R*Tree indexing, enabling rapid SQL queries, programmatic thematic choropleths, and inter-censal population density gradient analytics.

---

## 🔬 Database Architecture & ETL Pipeline

```mermaid
flowchart TD
    subgraph INP["1. Multi-Decadal Raw Census Ingestion (GSS & HDX)"]
        A["📊 2010 Tabular Census Reports & Disjoint Shapefiles<br/>(Historical 10-Region Baseline)"]
        B["📈 2021 Ghana Population & Housing Census<br/>(GSS StatsBank API / Modern 16-Region Framework)"]
    end

    subgraph ETL["2. Spatial ETL & Boundary Reconciliation"]
        A & B --> C["⚙️ Automated 10 ➔ 16 Region Boundary Reconciliation"]
        C --> D["📐 Demographic Field Normalization & Primary Key Matching"]
        D --> E["🧩 Topological Repair & Spatial Intersection Joins"]
    end

    subgraph GPKG["3. High-Performance OGC GeoPackage (ghana_census_2021.gpkg)"]
        E --> L0["Layer 0: adm0_country (National Extent)"]
        E --> L1["Layer 1: adm1_regions (16 Regions + Inter-Censal Growth r)"]
        E --> L2["Layer 2: adm2_districts (261 Municipal/District Assemblies)"]
        L0 & L1 & L2 --> R["⚡ SQLite R*Tree Spatial Indexing for Sub-Millisecond SQL Queries"]
    end

    subgraph MAPS["4. Thematic Analytics & Programmatic Choropleths"]
        R --> F["🗺️ Automated Matplotlib / GeoPandas Choropleth Generator"]
        R --> G["📊 Spatial Inequality & Density Gradient Metrics"]
    end

    style INP fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style ETL fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc
    style GPKG fill:#022c22,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style MAPS fill:#064e3b,stroke:#22c55e,stroke-width:2px,color:#f8fafc
```

### 1. Inter-Censal Growth Rate Formulation
For every district and region, the annualized geometric growth rate ($r$) between $2010$ and $2021$ is computed:
$$P_{2021} = P_{2010} \cdot (1 + r)^t \implies r = \left( \frac{P_{2021}}{P_{2010}} \right)^{\frac{1}{11}} - 1$$

### 2. Population Density Gradient
$$\text{Density} = \frac{\text{Total Population}}{\text{Geometric Area } [\text{km}^2]}$$

---

## 📂 Project Structure

```text
19_Census_GeoPackage_Spatial_Engine/
├── README.md                      <-- Comprehensive project report (You are here)
├── requirements.txt               <-- Python dependencies
└── scripts/
    ├── create_gis_database.py     <-- Compiles multi-layer OGC GeoPackage database
    ├── build_historical_gis.py    <-- Harmonizes 2010 vs 2021 administrative geometries
    ├── generate_thematic_maps.py  <-- Programmatic choropleth map generator
    ├── export_to_shapefiles.py    <-- Interoperability export utility
    ├── get_hdx_data.py            <-- Automated Humanitarian Data Exchange ingestion
    ├── query_2010_data.py         <-- SQL query utility for historical records
    └── query_statsbank.py         <-- Automated API client for GSS StatsBank
```

---

## ⚡ Quickstart

```bash
cd 19_Census_GeoPackage_Spatial_Engine
pip install -r requirements.txt
python scripts/create_gis_database.py
```
