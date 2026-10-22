# 🌍 GeoAI: Geospatial Artificial Intelligence & Deep Learning

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-API-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![TorchGeo](https://img.shields.io/badge/TorchGeo-0.5+-green?logo=python&logoColor=white)](https://github.com/microsoft/torchgeo)
[![Cyber2A Arctic](https://img.shields.io/badge/Cyber2A%20Challenge-Rank%20%235%20Global%20(16.45%20AP)-20BEFF?logo=kaggle&logoColor=white)](https://huggingface.co/spaces/cyber2a/2026GeoAIArcticChallenge)
[![Status: Maintained](https://img.shields.io/badge/Status-Maintained-brightgreen?logo=git&logoColor=white)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Author:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, CGPA 3.82/4.00) — University of Cape Coast, Ghana*  
> 🔗 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo) | ✉️ [Email](mailto:emmanuelyerbo@gmail.com)

---

## 📌 Executive Summary

This repository serves as the central research and engineering codebase for **Geospatial Artificial Intelligence (GeoAI)**, Earth Observation (EO), and Geospatial Deep Learning workflows. It features end-to-end implementations ranging from custom **1D/2D Convolutional Neural Networks (CNNs)**, **Vision Transformers (SegFormer, Swin)**, and **Geospatial Foundation Models (SAMGeo, DINOv3)** to large-scale **Google Earth Engine (GEE)** cloud pipelines and **PySAL spatial autocorrelation statistics**.

Every pipeline prioritizes **spatial validation rigor** (anti-leakage spatial block cross-validation), **geomorphometric feature engineering**, and **zero-retraining spatial/temporal transferability**.

---

## 🚀 Flagship Project Portfolio

| # | Project | Backbones & Architectures | Data Modalities & Sensors | Primary Metrics / Results | Folder |
|---|---|---|---|---|---|
| **01** | **VegHealthCNN** | Custom 1D-CNN (57k params), Cosine Annealing, AdamW | Sentinel-2 L2A (14-band spectral index tensor) | **98.7% Test Acc** (Spatial Block CV), saved 19.5% N fertilizer | [`01_VegHealthCNN/`](./01_VegHealthCNN) |
| **02** | **FrostWatch Arctic** | 3-Arm Ensemble: UNet++ (SE-ResNeXt50) + DeepLabV3+ (EffNet-B5) + MAnet (MiT-B5) | Arctic VHR Multispectral (13-ch geomorphometric tensor) | **Top 5 Internationally (16.45 AP)** on Cyber2A Challenge | [`02_FrostWatch_Arctic/`](./02_FrostWatch_Arctic) |
| **03** | **Building Footprint Extraction** | SegFormer-B3, DINOv3, U-Net, TorchGeo | 30cm Very High Resolution (VHR) Aerial / Satellite | Multi-region extraction across Ghana; ONNX runtime inference | [`03_Building_Extraction/`](./03_Building_Extraction) |
| **04** | **XAI Flood Inundation** | Custom U-Net + Grad-CAM Interpretability | Sub-meter UAV Aerial Drone Imagery | **87% Acc / 72% IoU**; validated on Akosombo Dam spillage | [`04_XAI_Flood_GradCAM/`](./04_XAI_Flood_GradCAM) |
| **05** | **Vision Transformer LULC** | SegFormer & Swin Transformer | Sentinel-2 Multi-temporal (2020–2026) | Shifted-window attention resolving mixed agro-pastoral mosaics | [`05_Vision_Transformer_LULC/`](./05_Vision_Transformer_LULC) |
| **06** | **SAMGeo Foundation Models** | Meta SAM (Segment Anything) + ViT Backbones | High-resolution Aerial Orthomosaics | Zero-shot and prompt-based structural building footprint extraction | [`06_SAMGeo_Infrastructure/`](./06_SAMGeo_Infrastructure) |
| **07** | **GEE Flood Susceptibility** | Multi-Criteria Weighted Overlay Pipeline | SRTM 30m, MERIT Hydro, JRC Water, WorldCover 10m | **37.5% High Flood Risk Zonation**; validated against NADMO records | [`07_GEE_Flood_Susceptibility/`](./07_GEE_Flood_Susceptibility) |
| **08** | **PySAL LST Hotspot Modeling** | Getis-Ord $G_i^*$, Anselin LISA, Rasterio | Landsat 7/8/9 Thermal Infrared (TIR) Collection 2 | 20-year UHI hotspot trajectory ($p < 0.01$) across Accra Metro | [`08_PySAL_LST_Hotspots/`](./08_PySAL_LST_Hotspots) |
| **09** | **Pedestrian Accessibility (15-Min City)** | OSMnx, NetworkX Dijkstra, Convex Hulls, PyDeck | OpenStreetMap Walk Network (`G_walk`), Healthcare POIs | Isochrone catchments, Healthcare Desert isolation, 3D WebGL | [`09_Network_Accessibility_15MinCity/`](./09_Network_Accessibility_15MinCity) |
| **10** | **Harmattan Bushfire Forecasting (CMPF)** | VideoMAEv2 (3D Tubelet Transformer), MViTv2, Cross-Modal Progressive Fine-Tuning | VIIRS 375m, Sentinel-2 L2A, ERA5-Land Wind/Temp, SRTM Slope | Spatiotemporal fire spread forecasting ($t+24\text{h}$) across Northern Ghana savannah | [`10_Spatiotemporal_Bushfire_VideoMAE/`](./10_Spatiotemporal_Bushfire_VideoMAE) |

---

## 🔬 Core Methodological Innovations

### 1. Spatial Block Cross-Validation (Zero Data Leakage)
Standard random train/test splits severely inflate model performance in spatial data science due to **spatial autocorrelation** (Tobler's First Law of Geography). Throughout this repository:
- Pixels are never randomly split.
- Training and evaluation domains are partitioned into **geographic blocks** (e.g., $0.01^\circ \times 0.01^\circ$ spatial grid cells) using `GroupKFold`.
- Spatially contiguous blocks are held out entirely, ensuring that test metrics reflect true spatial generalization.

```
+-------------------+-------------------+
|   TRAIN BLOCK 1   |    HELD-OUT TEST  |  <-- Zero spatial leakage
|    (Fold 0/1/2)   |      (Fold 3)     |      across boundary
+-------------------+-------------------+
|   TRAIN BLOCK 2   |   TRAIN BLOCK 3   |
|    (Fold 0/1/3)   |    (Fold 0/2/3)   |
+-------------------+-------------------+
```

### 2. Multi-Modal Geomorphometric Tensor Engineering
Raw multispectral bands alone often fail to capture subtle terrain deformities. In projects like **FrostWatch**, raw spectral bands are concatenated with first- and second-order geomorphometric derivatives into 13-channel tensors:
$$\text{Tensor} = \Big[ B_1, \dots, B_8, \;\text{Sobel Slope}, \;\text{Laplacian Curvature}, \;\text{IOR}, \;\text{NDVI} \times \text{Slope}, \;\text{Elevation} \Big]$$

### 3. Size-Weighted Area-Attenuated Loss
For targets with severe instance scale disparity (e.g., small thaw slumps vs. massive retrogressive scars):
$$\mathcal{L}_{\text{total}} = \alpha \cdot \mathcal{L}_{\text{Focal}} + \beta \cdot \mathcal{L}_{\text{Dice}} \cdot \omega(A)$$
where $\omega(A)$ dynamically scales gradients up to $8\times$ on small instances while preserving boundary precision.

### 4. Explainable GeoAI (XAI)
To prevent "black-box" shortcut learning, models are coupled with **Grad-CAM** and **DeepSHAP** backpropagation hooks. This verifies that neural activations correspond to hydrological, geomorphological, or vegetative boundaries rather than sensor artifacts or cloud edges.

### 5. Cross-Modal Progressive Fine-Tuning (CMPF)
Adapting pre-trained **Video Foundation Models (VideoMAEv2 & MViTv2)** to multi-modal spatiotemporal Earth Observation tasks (Li et al., IEEE TGRS 2026). Leverages 3D tubelet tokenization over continuous 5-day observation cubes ($T \times C \times H \times W$), bypassing domain gaps via modified patch projection ($E'_{patch}$) and intermediate geospatial adaptation.

---

## 📂 Repository Structure

```text
GEOAI/
├── README.md                              <-- Master repository showcase (You are here)
│
├── 01_VegHealthCNN/                       <-- Flagship Precision Agriculture & 1D-CNN
│   ├── README.md                          <-- Full technical report, architecture, & results
│   ├── notebooks/                         <-- VegHealthCNN_Pipeline.ipynb
│   └── results/                           <-- 2024 vs 2025 maps, Spatial Block CV, VRA prescription
│
├── 02_FrostWatch_Arctic/                  <-- Top 5 Cyber2A Permafrost Thaw Slump Segmentation
│   ├── README.md                          <-- 3-arm ensemble design, loss formulation, AP tables
│   ├── src/                               <-- Dataset loader, 13-channel tensor builder, losses
│   └── results/                           <-- Leaderboard proof, segmentation mask visualizer
│
├── 03_Building_Extraction/                <-- SegFormer-B3 & Foundation Models (TorchGeo)
│   ├── README.md                          <-- ONNX export benchmark, regularization algorithms
│   └── notebooks/                         <-- building_extraction_torchgeo.ipynb
│
├── 04_XAI_Flood_GradCAM/                  <-- Explainable AI U-Net
│   ├── README.md                          <-- Grad-CAM heatmaps, drone transfer evaluation
│   ├── src/                               <-- unet_model.py, gradcam_engine.py
│   └── results/                           <-- Akosombo dam spillage aerial drone test
│
├── 05_Vision_Transformer_LULC/            <-- SegFormer & Swin Transformer for Land Cover
│   ├── README.md                          <-- Shifted window attention analysis
│   └── notebooks/                         <-- transformer_lulc_pipeline.ipynb
│
├── 06_SAMGeo_Infrastructure/              <-- Segment Anything Geospatial Foundation Model
│   ├── README.md                          <-- Zero-shot / prompt-based infrastructure extraction
│   └── scripts/                           <-- samgeo_inference.py
│
├── 07_GEE_Flood_Susceptibility/           <-- Cloud Multi-Criteria Weighted Overlay (GEE)
│   ├── README.md                          <-- Multi-criteria ranking matrix & zonation map
│   └── scripts/                           <-- gee_flood_model.js
│
├── 08_PySAL_LST_Hotspots/                 <-- Spatial Autocorrelation & Urban Heat Island
│   ├── README.md                          <-- Landsat split-window LST & Getis-Ord Gi* analysis
│   └── scripts/                           <-- pysal_hotspot_pipeline.py
│
├── 09_Network_Accessibility_15MinCity/    <-- Pedestrian Accessibility & 15-Minute City
│   ├── README.md                          <-- 6-Scenario Accessibility Case Study & WebGL Pydeck
│   └── src/                               <-- isochrone_walk_engine.py
│
└── 10_Spatiotemporal_Bushfire_VideoMAE/   <-- Video Foundation Model & CMPF (Li et al., 2026)
    ├── README.md                          <-- VideoMAEv2 / MViTv2 Spatiotemporal Bushfire Forecasting
    ├── scripts/                           <-- gee_export_bushfire_tensors.js (Cloud data pipeline)
    └── src/                               <-- model_videomae.py, losses.py
```

---

## 🛠️ Geospatial & AI Tech Stack

- **Deep Learning Frameworks:** `PyTorch`, `PyTorch Lightning`, `TorchGeo`, `segmentation_models_pytorch` (SMP), `timm`, `Hugging Face Transformers`, `TensorFlow/Keras`, `Ultralytics (YOLO)`.
- **Architectures:** 1D-CNN, VideoMAEv2 (3D Tubelet Transformer), MViTv2, SegFormer (MiT), Swin Transformer, Segment Anything Model (SAMGeo), DINOv3, U-Net, UNet++, DeepLabV3+, MAnet, ResNet, EfficientNet.
- **Explainability & Validation:** `Grad-CAM`, `DeepSHAP`, `Spatial Block Cross-Validation` (GroupKFold), `Size-Weighted Focal+Dice Loss`, `Class-Balanced Focal Loss`, `LoRA (PEFT)`.
- **Geospatial & Cloud Platforms:** `Google Earth Engine` (JavaScript & Python API), `Digital Earth Africa`, `ArcGIS Pro`, `QGIS`, `PostGIS`, `Kaggle` (2×T4 GPUs).
- **Spatial Data Science Libraries:** `GeoPandas`, `Rasterio`, `RioXarray`, `xarray`, `PySAL` (`libpysal`, `esda`, `spreg`), `OSMnx`, `Leafmap`, `Geemap`, `Shapely`, `PySTAC`, `rasterstats`.
- **Languages:** `Python` (Primary), `JavaScript` (GEE), `R`, `SQL` (PostGIS).

---

## ⚡ Quickstart & Reproducibility

### 1. Clone the Repository
```bash
git clone https://github.com/Emmanuel-Yerbo/GEOAI.git
cd GEOAI
```

### 2. Set Up Python Environment
```bash
conda create -n geoai python=3.11 -y
conda activate geoai
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install geopandas rasterio rioxarray torchgeo segmentation-models-pytorch pysal earthengine-api
```

### 3. Run a Project Pipeline (Example: VegHealthCNN)
```bash
cd 01_VegHealthCNN
jupyter notebook notebooks/VegHealthCNN_Pipeline.ipynb
```

---

## 📢 Conference Presentation & Paper Citation

This research was accepted and presented as an oral presentation at the **GeoAI for Sustainable Development Conference (GeoAI4SD 2026)**:

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
