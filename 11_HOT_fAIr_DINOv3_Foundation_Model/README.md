# HOT fAIr Foundation Model: DINOv3-S + UperNet Building Footprint Extraction
## Nationwide Building Footprint Extraction with Self-Supervised Vision Transformers

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch 2.4](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Backbone: DINOv3-S](https://img.shields.io/badge/Backbone-Meta%20DINOv3--ViT--S%2F16-blueviolet)](https://github.com/facebookresearch/dinov2)
[![Decoder: UperNet](https://img.shields.io/badge/Decoder-UperNet%20FPN%2BPPM-blue)](https://github.com/open-mmlab/mmsegmentation)
[![Inference: ONNX Runtime](https://img.shields.io/badge/Inference-ONNX%20Opset%2017-005CED?logo=onnx&logoColor=white)](https://onnxruntime.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## ⚡ Executive Summary

1. **The Core Spatial Problem**: Conventional building footprint segmentation models across Sub-Saharan Africa struggle in high-density informal settlements. Standard convolutional neural networks frequently merge adjacent corrugated zinc roofs separated by narrow alleys ($< 1.5\text{ m}$) into amorphous blobs, while confusing dry laterite soils with weathered roofs.
2. **The Foundation Model Architecture**: We engineered a Geospatial Foundation Model adaptation for high-resolution building footprint extraction across tropical African built environments. The pipeline couples a self-supervised **Meta DINOv3-ViT-S/16** encoder with a multi-scale **UperNet** decoder (Feature Pyramid Network + Pyramid Pooling Module) and a 3-head geometric regularization engine (footprint logits, boundary contours, and signed distance fields).
3. **Core Output**: The system exports regularized building polygons and optimized ONNX runtime graphs for low-latency edge and server-side cadastral mapping.

---

## 🔬 Architectural Workflow

```mermaid
flowchart LR
    A["VHR Aerial Orthomosaic (30–50cm)"] --> B["DINOv3-ViT-S/16 Backbone"] --> C["Multi-Scale UperNet Decoder"] --> D["Multi-Task Geometric Heads"] --> E["Cadastral Building Polygons"]
```

#### 1. Self-Supervised Foundation Encoder (DINOv3-ViT-S/16)
- **The Process**: Uses a self-supervised Vision Transformer with $14 \times 14$ patch projections ($D = 384$). Early representation blocks are frozen to retain foundational Earth Observation visual priors, while upper blocks are differentially fine-tuned to adapt to tropical roof textures.
- **The Essence**: Captures global context across entire residential settlements while maintaining sub-meter spatial localization along structural eaves.

#### 2. Multi-Scale UperNet Decoder (FPN + PPM)
- **The Process**: Extracts feature representations at multiple spatial pyramid scales ($1/4, 1/8, 1/16, 1/32$), passing them through a Pyramid Pooling Module (PPM) with multi-scale pooling bins ($1\times 1, 2\times 2, 3\times 3, 6\times 6$).
- **The Essence**: Squeezes multi-resolution context to prevent small detached buildings from vanishing while maintaining sharp structural perimeters.

#### 3. Multi-Task Geometric Heads
- **Head 1 (Footprint Logits)**: Optimizes footprint area overlap via combined BCE and Soft Dice loss.
- **Head 2 (Boundary Contour)**: High-gradient edge isolation along exterior eaves ($w_{\text{bnd}} = 0.43$).
- **Head 3 (Signed Distance Field)**: Smooth Huber loss on Euclidean centroid offsets ($w_{\text{dst}} = 0.52$) to guarantee physical separation between contiguous roofs.

---

## 🖼️ Empirical Building Segmentation Visuals

### Multi-Biome Cross-Regional Building Extraction Across Ghana
The pipeline was evaluated across three distinct Ghanaian eco-zones to verify cross-regional adaptability:

<p align="center">
  <img src="results/accra_coastal_building_extraction.jpg" width="32%" alt="Accra Coastal Dense Core Building Footprints">
  <img src="results/kumasi_forest_building_extraction.jpg" width="32%" alt="Kumasi Forest Belt Metropolitan Extraction">
  <img src="results/tamale_savannah_building_extraction.jpg" width="32%" alt="Northern Savannah Compound Housing">
</p>

| Eco-Zone | Geographic Region | Architectural Morphology & Roof Materials |
|---|---|---|
| **Coastal Plains** | Greater Accra Metropolitan Area | Ultra-dense informal settlements, multi-story concrete, zinc/tin roofs |
| **Tropical Forest** | Kumasi Metropolitan Area | Dense commercial cores, residential compounds, shaded canopy margins |
| **Guinea Savannah** | Tamale / Northern Region | Circular & rectangular mud-brick compounds, thatched roofs, bright laterite soils |

---

### Roof Segmentation & Instance Boundary Predictions

<p align="center">
  <img src="results/ghana_roof_segmentation_predictions.jpg" width="60%" alt="Ghana Roof Segmentation Predictions and Bounding Instances">
</p>

> **Above**: Instance-level roof segmentation masks capturing rooftop pitch lines, compound geometries, and perimeter boundaries across complex residential fabrics.

---

## 📐 Mathematical Formulation & Loss Objectives

The model is trained using a compound multi-task objective that simultaneously optimizes footprint area overlap, sharp boundary gradients, and geometric distance transforms:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCE}}(\hat{Y}_{\text{mask}}, Y) + \mathcal{L}_{\text{Dice}}(\hat{Y}_{\text{mask}}, Y) + w_{\text{bnd}} \cdot \mathcal{L}_{\text{BCE}}(\hat{Y}_{\text{bnd}}, B) + w_{\text{dst}} \cdot \mathcal{L}_{\text{Huber}}(\tanh(\hat{Y}_{\text{dst}}), D)$$

Where:
- $\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum \hat{Y} Y + \epsilon}{\sum \hat{Y} + \sum Y + \epsilon}$ penalizes class imbalance in sparsely built areas.
- $w_{\text{bnd}} = 0.43$ enforces high-frequency edge isolation along eaves and exterior walls.
- $w_{\text{dst}} = 0.52$ optimizes the signed Euclidean distance transform to guarantee distinct separation between contiguous roofs.
- $\mathcal{L}_{\text{Huber}}$ ($\delta = 1.0$) prevents gradient explosion from extreme distance outliers.

### Differential Learning Rate Protocol
$$\eta_{\theta} = \begin{cases} 0 & \text{Blocks 0–7 (Frozen Base)} \\ 1 \times 10^{-5} & \text{Blocks 8–11 (Transformer Adaptation)} \\ 1 \times 10^{-4} & \text{UperNet Neck + Geometric Heads} \end{cases}$$

---

## 📂 Repository Structure & Artifacts

```text
11_HOT_fAIr_DINOv3_Foundation_Model/
├── README.md                                 <-- Project documentation (You are here)
├── requirements.txt                          <-- Dependencies (PyTorch, timm, albumentations, onnx)
├── results/                                  <-- Empirical evaluation figures & segmented visuals
│   ├── accra_coastal_building_extraction.jpg <-- Full-scene Accra coastal metropolitan footprint layer
│   ├── kumasi_forest_building_extraction.jpg <-- Kumasi forest belt building footprint layer
│   ├── tamale_savannah_building_extraction.jpg <-- Tamale Guinea savannah compound housing layer
│   └── ghana_roof_segmentation_predictions.jpg <-- Instance-level roof predictions
└── notebooks/
    ├── hot_dinov3s_ghana_pipeline.ipynb      <-- Training, multi-task loss & inference pipeline
    └── hot_fair_ghana_benchmark.ipynb        <-- Multi-regional evaluation across Ghana biomes
```

---

## ⚡ Quickstart & Reproducibility

### 1. Environment Setup
```bash
cd 11_HOT_fAIr_DINOv3_Foundation_Model
pip install -r requirements.txt
```

### 2. Run Pipeline Notebook
```bash
jupyter notebook notebooks/hot_dinov3s_ghana_pipeline.ipynb
```

### 3. Production ONNX Inference & Export
```python
import onnxruntime as ort
import numpy as np

# Load optimized ONNX runtime session
session = ort.InferenceSession("ghana_dinov3s_building_extractor.onnx", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

# Run inference on normalized VHR patch (1, 3, 256, 256)
input_tensor = np.random.randn(1, 3, 256, 256).astype(np.float32)
outputs = session.run(None, {session.get_inputs()[0].name: input_tensor})
footprint_logits, boundary_logits, distance_field = outputs[0], outputs[1], outputs[2]
```

---

## 📜 Research Attribution

```bibtex
@misc{yerbo2025hotfairghana,
  author       = {Emmanuel Yerbo},
  title        = {Nationwide Building Footprint Extraction with Self-Supervised Vision Transformers: DINOv3-S + UperNet Foundation Model for Ghana},
  year         = {2025},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/11_HOT_fAIr_DINOv3_Foundation_Model}},
  note         = {ORCID: 0009-0008-8968-6999}
}
```
