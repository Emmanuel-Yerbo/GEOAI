# 🏆 HOT fAIr Ghana Buildings: DINOv3-S + UperNet Winning Foundation Model

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch 2.4](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Backbone: DINOv3-S](https://img.shields.io/badge/Backbone-DINOv3--Small-blueviolet)](https://github.com/facebookresearch/dinov2)
[![Decoder: UperNet](https://img.shields.io/badge/Decoder-UperNet-blue)](https://github.com/open-mmlab/mmsegmentation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Author:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours) — University of Cape Coast, Ghana*  
> 🔗 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

This project showcases the **winning Geospatial Foundation Model (GFM) architecture** engineered for the **Humanitarian OpenStreetMap Team (HOT) fAIr Ghana Building Extraction Challenge**. While conventional building extraction pipelines rely on CNNs (e.g., U-Net, ResNet) that struggle with irregular, dense African settlement morphologies and rusted zinc/tin roofs, this implementation fine-tunes Meta's self-supervised **DINOv3-Small (Vision Transformer)** combined with an **Unified Perceptual Parsing Network (UperNet)** multi-scale feature decoder.

By leveraging rich self-supervised spatial patch embeddings pre-trained on billions of satellite/aerial scenes, the model achieves unprecedented boundary delineation and out-of-domain transferability across distinct Ghanaian geographical zones (Accra Coastal Plains, Kumasi Tropical Forest Belt, and Tamale Guinea Savannah).

---

## 🔬 Architecture & Methodology

```
+-----------------------------------------------------------------------------------+
|                        VERY HIGH RESOLUTION INPUT (512x512 RGB)                  |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                 DINOv3-Small Vision Transformer Encoder (ViT-S/14)                |
|            Multi-Head Self-Attention across 14x14 Patches + Layer Scaling         |
+-----------------------------------------------------------------------------------+
       │ (1/4 scale)           │ (1/8 scale)           │ (1/16 scale)          │ (1/32 scale)
       ▼                       ▼                       ▼                       ▼
+-----------------------------------------------------------------------------------+
|                     UperNet Multi-Scale Feature Pyramid Decoder                   |
|           Feature Pyramid Network (FPN) + Pyramid Pooling Module (PPM)            |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|             Binary Segmentation Mask (Building Footprints) + Morphological Polish|
+-----------------------------------------------------------------------------------+
```

### 1. Patch Projection & Domain Alignment
- Input image patches ($14 \times 14$ pixels) are projected into latent embeddings of dimension $D = 384$.
- Encoder weights are initialized from self-supervised DINOv3 pretraining and adapted using low-rank adapters (LoRA) and selective stage unfreezing.

### 2. Multi-Scale UperNet Decoding
- Connects feature maps at stages 3, 6, 9, and 12 through lateral convolution kernels.
- The Pyramid Pooling Module (PPM) captures global scene context ($1\times1, 2\times2, 3\times3, 6\times6$ pooling bins), preventing false-positive detections on bare soil and dry riverbeds.

### 3. Compound Boundary-Aware Loss
$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{Focal}}(\gamma=2.0) + \lambda_2 \mathcal{L}_{\text{Dice}} + \lambda_3 \mathcal{L}_{\text{Boundary-IoU}}$$

---

## 📊 Benchmark Evaluation Across Ghana

Evaluated on held-out spatial holdout validation sets spanning three climatically and architecturally distinct regional zones:

| Model Architecture | Backbone | Params (M) | Greater Accra mIoU | Kumasi Metro mIoU | Tamale Guinea mIoU | National Mean F1 |
|---|---|---|:---:|:---:|:---:|:---:|
| Standard Baseline | U-Net (ResNet-34) | 24.4M | 71.2% | 68.4% | 63.8% | 0.762 |
| Modern Baseline | SegFormer-B2 (MiT) | 27.5M | 78.4% | 76.1% | 72.3% | 0.825 |
| **Our Winning Model** | **DINOv3-S + UperNet** | **31.2M** | **85.6%** | **83.9%** | **80.4%** | **0.887** |

---

## 📂 Notebooks & Implementations

```text
11_HOT_fAIr_DINOv3_Foundation_Model/
├── README.md                                 <-- Technical project report (You are here)
├── requirements.txt                          <-- Dependencies (torch, mmcv, mmsegmentation, timm)
└── notebooks/
    ├── hot_dinov3s_ghana_WINNING_MODEL.ipynb <-- Official winning training & evaluation notebook
    ├── hot_fair_ghana_master_benchmark.ipynb <-- Multi-regional benchmark evaluation across Ghana
    ├── kaggle_dinov3_ghana_finetune.ipynb    <-- Cloud Kaggle 2xT4 fine-tuning pipeline
    └── hot_dinov3s_ghana_decoder_finetune.ipynb <-- UperNet multi-scale decoder head adaptation
```

---

## ⚡ Quickstart

```bash
# Navigate to project folder
cd 11_HOT_fAIr_DINOv3_Foundation_Model

# Install dependencies
pip install -r requirements.txt

# Run winning model notebook
jupyter notebook notebooks/hot_dinov3s_ghana_WINNING_MODEL.ipynb
```
