# 🛰️ 10_Spatiotemporal_Bushfire_VideoMAE: Adapting Video Foundation Models for Savannah Bushfire Forecasting via Cross-Modal Progressive Fine-Tuning (CMPF)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch 2.4](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Foundation Model: VideoMAEv2](https://img.shields.io/badge/VFM-VideoMAEv2-blueviolet?logo=huggingface&logoColor=white)](https://github.com/OpenGVLab/VideoMAEv2)
[![IEEE TGRS 2026 Paradigm](https://img.shields.io/badge/Methodology-Li_et_al._(IEEE_TGRS_2026)-success)](https://ieeexplore.ieee.org)
[![Target: Northern Ghana](https://img.shields.io/badge/Geography-Northern_Savannah_Ghana-gold)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)  
> 📖 *Methodological Lineage: Adapted from the landmark framework by Wenwen Li, Chia-Yu Hsu, and Sizhe Wang (IEEE Transactions on Geoscience and Remote Sensing, Vol. 64, 2026): "Adapting Video Foundation Models for Spatiotemporal Wildfire Forecasting via Cross-Modal Progressive Fine-Tuning".*

---

## 📌 Executive Summary

Wildfires and dry-season bushfires across the Guinea and Sudan Savannah zones of **Northern Ghana** (Northern, Savannah, Upper East, and Upper West regions) cause widespread loss of subsistence grain crops, shea nut trees (*Vitellaria paradoxa*), and severe environmental degradation during the dry **Harmattan** season (November–April). 

Conventional 2D convolutional networks and static vision transformers process satellite passes as independent temporal snapshots, failing to capture the underlying continuous spatiotemporal physics of fire propagation driven by dynamic wind fields, fuel desiccation, and terrain gradients.

This project implements the **Cross-Modal Progressive Fine-Tuning (CMPF)** paradigm to adapt **Video Foundation Models (VideoMAEv2 & MViTv2)** for **next-day ($t + 24\text{h}$) active fire spread forecasting** across the Northern Ghana savannah belt.

```mermaid
flowchart LR
    A["Video Foundation Model (VideoMAEv2)"] --> B["Cross-Modal Patch Projection (11 Channels)"] --> C["Savannah Spatiotemporal Tuning"] --> D["Next-Day Fire Spread Forecast (t+24h)"]
```

---

## 🔬 Core Methodological Pillars

### 1. 3D Spatiotemporal Tubelet Tokenization
Unlike image-centric transformers that flatten frames along channel dimensions ($I \in \mathbb{R}^{H \times W \times (T \cdot C)}$), **VideoMAEv2** performs native **3D spatiotemporal tubelet patching**:
$$\text{Tokens} = \left(\frac{T}{t_p}\right) \times \left(\frac{H}{h_p}\right) \times \left(\frac{W}{w_p}\right)$$
This enables full joint space-time self-attention from layer 1, natively modeling how fire fronts propagate downwind as a function of fuel moisture and terrain slope.

### 2. Multi-Modal Physical Tensor ($T = 5$ days, $M = 11$ Channels)
Input tensors are constructed at a uniform $375\text{ m}$ spatial grid spanning 5 consecutive observation days ($T = 5$):

| Channel Index | Modality / Sensor | Variable | Physical Relevance |
|:---:|:---|:---|:---|
| **0** | **VIIRS (VNP14IMGTDL)** | Active Fire Mask ($S_t \in \{0, 1\}$) | Primary target propagation seed |
| **1** | **Sentinel-2 L2A** | Normalized Difference Moisture Index (NDMI) | Fuel desiccation & curing state |
| **2** | **Sentinel-2 L2A** | Normalized Difference Vegetation Index (NDVI) | Combustible biomass fuel load |
| **3** | **ERA5-Land (ECMWF)** | 10m U-component of Wind ($u_{10}$) | Zonal fire spread vector |
| **4** | **ERA5-Land (ECMWF)** | 10m V-component of Wind ($v_{10}$) | Meridional fire spread vector |
| **5** | **ERA5-Land (ECMWF)** | 2m Air Temperature ($T_{2m}$) | Thermal preheating of fuel |
| **6** | **ERA5-Land (ECMWF)** | Relative Humidity ($RH$) | Atmospheric moisture deficit |
| **7** | **ERA5-Land (ECMWF)** | Total Daily Precipitation ($P$) | Surface wetting / quenching |
| **8** | **SRTM 30m** | Topographic Elevation | Orographic atmospheric boundary |
| **9** | **SRTM 30m** | Topographic Slope | Preheating gradient (flames advance faster upslope) |
| **10** | **SRTM 30m** | Topographic Aspect | Solar radiation exposure |

### 3. Class-Balanced Focal Loss
Due to severe spatial sparsity (active fire pixels comprise $< 1.5\%$ of the landscape):
$$\mathcal{L}_{\text{Focal}} = -\alpha (1 - p_t)^\gamma \log(p_t), \quad \alpha = 0.75, \; \gamma = 2.0$$

---

## ⚡ Zero-Bottleneck Engineering Architecture (Optimized for Ghana)

To bypass local hardware constraints and internet bandwidth limits in West Africa:

1. **Cloud-First Preprocessing (GEE-to-Tensor):** All VIIRS co-registration, ERA5 re-gridding, and Sentinel-2 index computations execute entirely in the **Google Earth Engine (GEE)** cloud. Instead of downloading 150 GB of raw scenes, pre-stacked lightweight NumPy tensors (`.npz`, ~1.2 GB) are exported directly.
2. **Harmattan Cloud-Free Advantage:** The target active fire season occurs during the peak Harmattan (Dec–March), providing near-zero cloud occlusion over the Northern Savannah.
3. **Parameter-Efficient LoRA Fine-Tuning:** VideoMAEv2 (327M params) is adapted with **LoRA (Low-Rank Adaptation)** on query/key/value projection matrices ($r=8, \alpha=16$), freezing 98.5% of the backbone and training seamlessly on **Kaggle 2×T4 GPUs (16 GB VRAM)**.

---

## 📂 Folder Structure

```text
10_Spatiotemporal_Bushfire_VideoMAE/
├── README.md                          <-- Project technical specification (You are here)
├── requirements.txt                   <-- PyTorch, timm, einops, peft, rasterio
├── scripts/
│   └── gee_export_bushfire_tensors.js <-- GEE cloud script generating 11-channel space-time cubes
└── src/
    ├── model_videomae.py              <-- VideoMAEv2 adapted with E'_patch and LoRA adapters
    ├── losses.py                      <-- Class-balanced Focal Loss
    └── dataset.py                     <-- PyTorch Spatiotemporal Dataset loader (B, T, C, H, W)
```

---

## 📖 Citation & References

```bibtex
@article{li2026adapting,
  author    = {Li, Wenwen and Hsu, Chia-Yu and Wang, Sizhe},
  title     = {Adapting Video Foundation Models for Spatiotemporal Wildfire Forecasting via Cross-Modal Progressive Fine-Tuning},
  journal   = {IEEE Transactions on Geoscience and Remote Sensing},
  volume    = {64},
  pages     = {3000218},
  year      = {2026},
  publisher = {IEEE},
  doi       = {10.1109/TGRS.2026.3527265}
}
```
