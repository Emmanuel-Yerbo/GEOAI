# 🌍 GeoAI: Geospatial Artificial Intelligence & Deep Learning Research Suite

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch 2.4](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-API-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![TorchGeo](https://img.shields.io/badge/TorchGeo-0.5+-green?logo=python&logoColor=white)](https://github.com/microsoft/torchgeo)
[![Cyber2A Arctic](https://img.shields.io/badge/Cyber2A%20Challenge-Rank%20%235%20Global%20(16.45%20AP)-20BEFF?logo=kaggle&logoColor=white)](https://huggingface.co/spaces/cyber2a/2026GeoAIArcticChallenge)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--8968--6999-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-8968-6999)
[![Status: Production Suite](https://img.shields.io/badge/Status-20%20Projects%20Live-brightgreen?logo=git&logoColor=white)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio Web App](https://emmanuelyerbo.github.io/GEOAI) | ✉️ [Email](mailto:emmanuelyerbo@gmail.com)

---

## 📌 Executive Summary

This repository serves as the master research and engineering codebase for **Geospatial Artificial Intelligence (GeoAI)**, Earth Observation (EO), and Advanced Spatial Data Science. It integrates **20 end-to-end, reproducible research projects** bridging fundamental physical geomorphology, spaceborne LiDAR biophysics, and Discrete Global Grid Systems (DGGS) with state-of-the-art **Convolutional Neural Networks (1D/2D CNNs)**, **Vision Transformers (SegFormer, Swin)**, **Geospatial Foundation Models (Meta DINOv3, SAMGeo)**, and **Spatiotemporal Video Transformers (VideoMAEv2)**.

Every pipeline enforces strict **spatial validation rigor** (anti-leakage spatial block cross-validation), **geomorphometric tensor feature engineering**, and **zero-retraining spatial/temporal transferability**.

---

## 🚀 The 20-Project Research Portfolio

| # | Project Name | Primary Backbones & Architectures | Data Modalities & Sensors | Core Empirical Metrics / Results | Subfolder |
|---|---|---|---|---|:---:|
| **01** | **VegHealthCNN** | Custom 1D-CNN (57k params), Cosine Annealing, AdamW | Sentinel-2 L2A (14-band spectral index tensor) | **98.7% Test Acc** (Spatial Block CV); 19.5% N reduction | [`01_VegHealthCNN/`](./01_VegHealthCNN) |
| **02** | **FrostWatch Arctic** | 3-Arm Ensemble: UNet++ (SE-ResNeXt50) + DeepLabV3+ + MAnet | Arctic VHR Multispectral (13-ch geomorphometric tensor) | **Top 5 Globally (16.45 AP)** on Cyber2A Challenge | [`02_FrostWatch_Arctic/`](./02_FrostWatch_Arctic) |
| **03** | **Building Footprint Extraction** | SegFormer-B3, DINOv3, U-Net, TorchGeo | 30cm Very High Resolution (VHR) Aerial / Satellite | Multi-region footprint extraction; ONNX runtime benchmarks | [`03_Building_Extraction/`](./03_Building_Extraction) |
| **04** | **XAI Flood Inundation** | Custom U-Net + Grad-CAM Interpretability | Sub-meter UAV Aerial Drone Imagery | **87% Acc / 72% IoU**; validated on Akosombo Dam spillage | [`04_XAI_Flood_GradCAM/`](./04_XAI_Flood_GradCAM) |
| **05** | **Vision Transformer LULC** | SegFormer & Swin Transformer + XGBoost SHAP | Sentinel-2 Multi-temporal (2020–2026) | Shifted-window attention resolving mixed agro-pastoral mosaics | [`05_Vision_Transformer_LULC/`](./05_Vision_Transformer_LULC) |
| **06** | **SAMGeo Foundation Models** | Meta SAM (Segment Anything) + LangSAM ViT | High-resolution Aerial Orthomosaics | Zero-shot and text-prompted infrastructure extraction | [`06_SAMGeo_Infrastructure/`](./06_SAMGeo_Infrastructure) |
| **07** | **GEE Flood Susceptibility** | Multi-Criteria Cloud Weighted Overlay Pipeline | SRTM 30m, MERIT Hydro, JRC Water, WorldCover 10m | **37.5% High Flood Risk Zonation**; validated against NADMO | [`07_GEE_Flood_Susceptibility/`](./07_GEE_Flood_Susceptibility) |
| **08** | **PySAL LST Hotspot Modeling** | Getis-Ord $G_i^*$, Anselin LISA, Rasterio | Landsat 7/8/9 Thermal Infrared (TIR) Collection 2 | 20-year UHI hotspot trajectory ($p < 0.01$) across Accra Metro | [`08_PySAL_LST_Hotspots/`](./08_PySAL_LST_Hotspots) |
| **09** | **Pedestrian Accessibility (15-Min)** | OSMnx, NetworkX Dijkstra, Convex Hulls, PyDeck | OpenStreetMap Walk Network (`G_walk`), Healthcare POIs | Isochrone catchments, Healthcare Desert isolation, 3D WebGL | [`09_Network_Accessibility_15MinCity/`](./09_Network_Accessibility_15MinCity) |
| **10** | **Bushfire Forecasting (CMPF)** | VideoMAEv2 (3D Tubelet Transformer), MViTv2 | VIIRS 375m, Sentinel-2 L2A, ERA5-Land, SRTM Slope | Spatiotemporal fire spread forecasting ($t+24\text{h}$) across savanna | [`10_Spatiotemporal_Bushfire_VideoMAE/`](./10_Spatiotemporal_Bushfire_VideoMAE) |
| **11** | **HOT fAIr Foundation Model**| DINOv3-S + UperNet Decoder, Multi-Task Heads | VHR Optical Orthomosaics (30cm-50cm) | Multi-scale boundary isolation & distance transform regularized building footprints | [`11_HOT_fAIr_DINOv3_Foundation_Model/`](./11_HOT_fAIr_DINOv3_Foundation_Model) |
| **12** | **GeoNLP Accident Geocoding** | spaCy NER, Levenshtein Fuzzy Gazetteers | Online news feeds, Google News RSS, Leaflet | Automated crash extraction & spatial blackspot heatmapping | [`12_GeoNLP_Spatial_Accident_Geocoding/`](./12_GeoNLP_Spatial_Accident_Geocoding) |
| **13** | **H3 Hexagonal Spatial Intelligence**| Uber H3 DGGS, Multi-Resolution Binning (Res 7-9) | OpenStreetMap, GSS Census, POI distributions | Uniform 6-neighbor spatial tessellation; eliminates MAUP | [`13_H3_Hexagonal_Spatial_Intelligence/`](./13_H3_Hexagonal_Spatial_Intelligence) |
| **14** | **Coastal Shoreline Dynamics (DSAS)**| USGS DSAS v5.0, GeoPandas, Transect Engine | Multi-epoch historical shorelines (1986–2024) | Net Shoreline Movement (NSM) & End Point Rate (EPR) maps | [`14_Coastal_Shoreline_Dynamics_DSAS/`](./14_Coastal_Shoreline_Dynamics_DSAS) |
| **15** | **Spaceborne LiDAR Biomass (GEDI)** | NASA GEDI L4A LiDAR + Sentinel-2 MSI Fusion | Spaceborne waveform heights ($RH_{50}, RH_{98}$) | Multi-sensor allometric power-law regressor for canopy biomass density | [`15_Spaceborne_LiDAR_Biomass_GEDI/`](./15_Spaceborne_LiDAR_Biomass_GEDI) |
| **16** | **Nighttime Lights Socioeconomic EO** | NASA VIIRS Day/Night Band (DNB) Black Marble | Nocturnal radiance composites (15 arc-sec), R `terra` | Electrification corridor mapping & economic inequality indices | [`16_Nighttime_Lights_Socioeconomic_EO/`](./16_Nighttime_Lights_Socioeconomic_EO) |
| **17** | **3D Digital Twin & Morphometrics** | PyDeck WebGL 3D, Momepy Tessellation | OSM vector building footprints, road networks | Volumetric building extrusions & street orientation polar roses | [`17_3D_DigitalTwin_Urban_Morphometrics/`](./17_3D_DigitalTwin_Urban_Morphometrics) |
| **18** | **Hydrological Geomorphometry** | DEM D8 Flow Routing, Strahler Stream Hierarchy | NASA SRTM 30m Digital Elevation Model | Basin drainage network extraction & Strahler topological hierarchy | [`18_Hydrological_Geomorphometry_Strahler/`](./18_Hydrological_Geomorphometry_Strahler) |
| **19** | **Census GeoPackage Spatial Engine** | OGC GeoPackage (`.gpkg`), SQLite Spatialite | Ghana Census (2010 vs 2021), HDX Boundary API | Unified 3-tier demographic database & choropleth generator | [`19_Census_GeoPackage_Spatial_Engine/`](./19_Census_GeoPackage_Spatial_Engine) |
| **20** | **Spectral Neural Network Baseline** | Multilayer Perceptron (MLP) & Random Forest | Sentinel-2 MSI (4-band raw reflectance vectors) | Foundational pixel-level spectral reflectance benchmark | [`20_Spectral_Neural_Network_Baseline/`](./20_Spectral_Neural_Network_Baseline) |

---

## 🔬 Core Methodological Innovations

### 1. Spatial Block Cross-Validation (Zero Data Leakage)
Standard random train/test splits severely inflate model performance in spatial data science due to **spatial autocorrelation** (Tobler's First Law of Geography). Throughout this repository:
- Pixels are never randomly split.
- Training and evaluation domains are partitioned into **geographic blocks** (e.g., $0.01^\circ \times 0.01^\circ$ spatial grid cells) using `GroupKFold`.
- Spatially contiguous blocks are held out entirely, ensuring that test metrics reflect true spatial generalization.

### 2. Multi-Modal Geomorphometric Tensor Engineering
Raw multispectral bands alone often fail to capture subtle terrain deformities. In projects like **FrostWatch** and **Bushfire Forecasting**, raw spectral bands are concatenated with first- and second-order geomorphometric derivatives into 13-channel tensors:
$$\text{Tensor} = \Big[ B_1, \dots, B_8, \;\text{Sobel Slope}, \;\text{Laplacian Curvature}, \;\text{IOR}, \;\text{NDVI} \times \text{Slope}, \;\text{Elevation} \Big]$$

### 3. Cross-Modal Progressive Fine-Tuning (CMPF)
Adapting pre-trained **Video Foundation Models (VideoMAEv2 & MViTv2)** to multi-modal spatiotemporal Earth Observation tasks (Li et al., IEEE TGRS 2026). Leverages 3D tubelet tokenization over continuous 5-day observation cubes ($T \times C \times H \times W$), bypassing domain gaps via modified patch projection ($E'_{patch}$) and intermediate geospatial adaptation.

### 4. Discrete Global Grid Systems (DGGS) & Hexagonal Topologies
By mapping urban phenomena onto **Uber H3** hexagonal apertures, all cells possess invariant 6-neighbor adjacency distances, resolving the Modifiable Areal Unit Problem (MAUP) and accelerating spatial lag modeling.

---

## 📂 Repository Structure

```text
GEOAI/
├── LICENSE                                    <-- MIT License
├── README.md                                  <-- Master repository showcase (You are here)
├── .gitignore                                 <-- Optimized Python / Geospatial Git exclusions
│
├── 01_VegHealthCNN/                           <-- Precision Agriculture 1D-CNN (GeoAI4SD 2026)
├── 02_FrostWatch_Arctic/                      <-- Cyber2A Top 5 Global Permafrost Thaw Slump Ensemble
├── 03_Building_Extraction/                    <-- SegFormer-B3 & Foundation Models (TorchGeo)
├── 04_XAI_Flood_GradCAM/                      <-- Explainable AI U-Net on Akosombo Dam Drone Spillage
├── 05_Vision_Transformer_LULC/                <-- SegFormer & Swin Transformer Multi-Temporal LULC
├── 06_SAMGeo_Infrastructure/                  <-- Segment Anything Geospatial Foundation Model
├── 07_GEE_Flood_Susceptibility/               <-- Google Earth Engine Multi-Criteria Weighted Overlay
├── 08_PySAL_LST_Hotspots/                     <-- PySAL Spatial Autocorrelation & UHI Hotspots
├── 09_Network_Accessibility_15MinCity/        <-- OSMnx Dijkstra 15-Minute City Walkability
├── 10_Spatiotemporal_Bushfire_VideoMAE/       <-- VideoMAEv2 CMPF Spatiotemporal Fire Spread
├── 11_HOT_fAIr_DINOv3_Foundation_Model/       <-- Winning DINOv3-S + UperNet Building Architecture
├── 12_GeoNLP_Spatial_Accident_Geocoding/      <-- Spatial NLP, Fuzzy Gazetteers & Accident Mapping
├── 13_H3_Hexagonal_Spatial_Intelligence/      <-- Uber H3 Discrete Global Grid System (DGGS)
├── 14_Coastal_Shoreline_Dynamics_DSAS/        <-- USGS DSAS Coastal Erosion & Accretion Dynamics
├── 15_Spaceborne_LiDAR_Biomass_GEDI/          <-- NASA GEDI Spaceborne LiDAR & Sentinel-2 Biomass
├── 16_Nighttime_Lights_Socioeconomic_EO/      <-- NASA VIIRS Black Marble R Spatial Cartography
├── 17_3D_DigitalTwin_Urban_Morphometrics/     <-- PyDeck 3D WebGL Extrusions & Momepy Tessellations
├── 18_Hydrological_Geomorphometry_Strahler/   <-- SRTM Flow Routing & Strahler Stream Hierarchy
├── 19_Census_GeoPackage_Spatial_Engine/       <-- OGC GeoPackage Multi-Decadal Census Database
├── 20_Spectral_Neural_Network_Baseline/       <-- Foundational Pixel-Based MLP / RF Ablation Baseline
│
└── docs/                                      <-- Interactive 4-Tier Web App for GitHub Pages
    ├── index.html
    ├── style.css
    └── app.js
```

---

## 🛠️ Complete Geospatial & AI Tech Stack

- **Deep Learning Frameworks:** `PyTorch`, `PyTorch Lightning`, `TorchGeo`, `segmentation_models_pytorch` (SMP), `timm`, `Hugging Face Transformers`, `TensorFlow/Keras`.
- **Architectures:** DINOv3-S, VideoMAEv2 (3D Tubelet Transformer), MViTv2, SegFormer (MiT), Swin Transformer, Segment Anything Model (SAMGeo / LangSAM), U-Net, UNet++, DeepLabV3+, MAnet, 1D-CNN, MLP.
- **Explainability & Validation:** `Grad-CAM`, `DeepSHAP`, `Spatial Block Cross-Validation` (GroupKFold), `Size-Weighted Focal+Dice Loss`, `LoRA (PEFT)`.
- **Spatial Data Science & Discrete Grids:** `GeoPandas`, `Rasterio`, `Shapely`, `PySAL` (`libpysal`, `esda`), `Uber H3` (`h3-py`), `Momepy`, `OSMnx`, `NetworkX`.
- **Cloud & Remote Sensing Engines:** `Google Earth Engine` (JavaScript & Python API), `Digital Earth Africa`, `QGIS`, `ArcGIS Pro`, `PostGIS / OGC GeoPackage`.
- **Languages:** `Python` (Primary), `JavaScript` (GEE), `R` (`terra`, `sf`, `ggplot2`), `SQL` (Spatialite).

---

## 📢 Conference Citation

```bibtex
@inproceedings{yerbo2026geoai,
  title     = {GeoAI-Driven Precision Health Classification and Variable-Rate 
               Nitrogen Prescribing in Ghana Using a 1D-CNN and Spatial Block 
               Cross-Validation},
  author    = {Yerbo, Emmanuel},
  booktitle = {Proceedings of the GeoAI for Sustainable Development Conference (GeoAI4SD)},
  year      = {2026},
  address   = {Cape Coast, Ghana},
  institution = {Department of Geography and Regional Planning, University of Cape Coast}
}
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Emmanuel Yerbo</b> • Geospatial AI & Earth Observation Specialist<br>
  Cape Coast, Central Region, Ghana • <a href="mailto:emmanuelyerbo@gmail.com">emmanuelyerbo@gmail.com</a>
</p>
