# 🌱 VegHealthCNN: 1D-CNN for Spectral-Temporal Crop Health Mapping

[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-Sentinel--2%20L2A-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![Spatial CV](https://img.shields.io/badge/Spatial%20Validation-0.01%C2%B0%20Blocks-blue)](https://scikit-learn.org/)
[![Conference](https://img.shields.io/badge/Presented-GeoAI4SD%202026-orange)](https://ucc.edu.gh/)

## 📌 Overview
VegHealthCNN is a lightweight **1D-Convolutional Neural Network (57,091 parameters)** designed for pixel-level crop health classification from Sentinel-2 Level-2A 14-band spectral-index stacks. 

### Key Innovations:
1. **Spatial Block Cross-Validation ($0.01^\circ$ geographic blocks, ~1.1 km):** Prevents spatial autocorrelation data leakage, achieving **98.7% test accuracy** on 301 spatially independent ground-truth samples.
2. **Dual-Axis Transferability:** Demonstrates zero-retraining generalization across space (Akaakuma training domain $	o$ Prestea Huni-Valley Municipality) and time (2024 $	o$ 2025).
3. **Environmental & Economic Impact:** Detected **370.31 km² of galamsey-induced vegetation loss** and formulated an NDRE-modulated Variable-Rate Application (VRA) nitrogen prescription saving **19.5% fertilizer (~4.02 million kg N)** across 172,334 hectares.

---

## 🏗️ Architecture
```
Input (14 spectral features)
  │
  ├── Conv1D (1 -> 32, k=3, p=1) -> BatchNorm -> ReLU -> Dropout(0.2)
  ├── Conv1D (32 -> 64, k=3, p=1) -> BatchNorm -> ReLU -> Dropout(0.3)
  ├── Conv1D (64 -> 128, k=3, p=1) -> BatchNorm -> ReLU -> Dropout(0.4)
  │
  ├── AdaptiveAvgPool1d(1) -> Flatten
  │
  ├── Linear(128 -> 64) -> ReLU -> Dropout(0.3)
  └── Linear(64 -> 3) -> Softmax [Healthy, Moderate Stress, No-Vegetation]
```

## 📊 Input Spectral Features (14 Bands)
- **Sentinel-2 L2A Reflectance:** Blue (B2), Green (B3), Red (B4), Red Edge 1 (B5), Red Edge 2 (B6), Red Edge 3 (B7), Narrow NIR (B8A), SWIR1 (B11), SWIR2 (B12).
- **Derived Vegetation Indices:** Enhanced Vegetation Index (EVI), Normalized Difference Moisture Index (NDMI), Soil Adjusted Vegetation Index (SAVI), Normalized Difference Red-Edge (NDRE), Bare Soil Index (BSI).

---

## 🗺️ Dual-Axis Transferability Results

| Metric | 2024 Baseline | 2025 Monitoring | Net Dynamics |
|---|---|---|---|
| **Healthy Vegetation** | 1,407.82 km² (77.85%) | 1,037.51 km² (57.37%) | **−370.31 km²** (Contraction) |
| **Moderate Stress** | 622.28 km² (34.41%) | 623.49 km² (34.48%) | **+1.21 km²** |
| **No-Vegetation (Galamsey/Bare)** | 86.25 km² (4.77%) | 147.35 km² (8.15%) | **+61.10 km²** (Degradation) |

---

## 🌾 Variable-Rate Application (VRA) Prescription
- **Blanket Uniform Rate (120 kg N/ha):** 20,680,080 kg N
- **VRA Dynamic Prescription:** 16,656,250 kg N
- **Total Fertilizer Saved:** **4,023,830 kg N (19.5% reduction)**

---

## ⚡ Quickstart
```bash
cd 01_VegHealthCNN
pip install -r requirements.txt
python src/model.py
```
