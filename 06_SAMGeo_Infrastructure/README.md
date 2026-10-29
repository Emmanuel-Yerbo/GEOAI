# Automated Feature Extraction with Foundation Models: SAMGeo & LangSAM
## Case Study: Zero-Shot Campus Infrastructure & Aviation Intelligence in Ghana

[![Segment Anything](https://img.shields.io/badge/Meta%20AI-Segment%20Anything-blue?logo=meta)](https://segment-anything.com/)
[![SAMGeo](https://img.shields.io/badge/SAMGeo-Segment%20Geospatial-green)](https://samgeo.gishub.org/)
[![LangSAM](https://img.shields.io/badge/LangSAM-Grounding%20DINO%20%2B%20SAM-orange)](https://github.com/luca-medeiros/lang-segment-anything)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

### ⚡ Executive Summary

1. **The Core Spatial Problem:** Traditional spatial asset extraction requires weeks of manual digitizing or hundreds of thousands of labeled training polygons that municipal assemblies in developing countries cannot afford to produce.
2. **The Technical Pipeline:** We operationalized Meta AI's Segment Anything Model (SAM) and LangSAM with Vision Transformer (ViT) backbones, applying text-prompted zero-shot semantic segmentation over sub-meter aerial orthomosaics across institutional and aviation infrastructure in Ghana.
3. **Core Capability:** The zero-shot pipeline extracts building boundaries and structural assets directly from raw imagery with **zero task-specific model retraining**, converting instance segmentation masks into georeferenced GeoJSON cadastral polygons.

---

### 1. Introduction: Foundation Models in Remote Sensing
In classical Earth Observation, extracting structural built features requires laborious manual polygon digitization or supervised training of CNNs on thousands of annotated tiles. This project implements **Geospatial Foundation Models (SAMGeo & LangSAM)**, adapting Meta AI's **Segment Anything Model (SAM)** and Vision Transformer (ViT) backbones to remote sensing imagery.

By utilizing **zero-shot learning** and **natural language prompt engineering**, we eliminate the need for task-specific training data while maintaining boundary precision across complex architectural and vehicular targets.

---

### 2. Methodological Pipeline & Promptable Vision Architecture

```mermaid
flowchart LR
    A["Aerial Orthomosaic"] --> B["ViT Image Encoder"] --> C["Prompt / Grounding DINO"] --> D["SAM Mask Decoder"] --> E["Cadastral GeoJSON"]
```

#### 2.1 Promptable Vision Transformer Inference (SAMGeo)
- **The Process**: We ingest sub-meter satellite/aerial imagery into pre-trained Vision Transformer backbones (`vit_h`, `vit_l`, `vit_b`). Image embeddings are computed once, and spatial masks are decoded in real-time.
- **The Essence**: ViT self-attention heads capture global spatial context and high-frequency structural edges simultaneously. This allows SAMGeo to delineate complex building footprints without edge degradation.

#### 2.2 Dual-Branch Natural Language Grounding (LangSAM)
- **The Process**: We pair **Grounding DINO** (open-vocabulary object detector) with **SAM** (segmentation engine). A natural language text prompt (e.g., `"Airplanes"`, `"Building"`) is passed to detect bounding boxes, which are instantly fed to SAM as geometric prompt coordinates.
- **The Essence**: Decouples semantic identification from pixel-level boundary refinement. Grounding DINO handles open-vocabulary localization, while SAM computes the high-precision instance mask.

---

### 3. Pipeline Implementation & Execution

The complete reproducible engine is implemented in `src/samgeo_langsam_engine.py`:

```python
from src.samgeo_langsam_engine import initialize_samgeo, detect_aircraft_with_langsam

# Initialize SAMGeo with Vision Transformer backbone
sam_engine = initialize_samgeo(model_type="vit_h")

# Run natural language zero-shot feature extraction
aviation_detector = detect_aircraft_with_langsam(
    image_path="data/orthomosaic_sample.tif",
    text_prompt="Airplanes",
    box_threshold=0.30,
    text_threshold=0.25
)
```

---

### 4. Operational & Planning Implications
Geospatial foundation models fundamentally change the economics of spatial intelligence:
1. **Rapid Disaster Damage Mapping:** Zero-shot building extraction enables emergency response teams to quantify structural collapses within minutes of new satellite acquisition.
2. **Aviation & Logistics Monitoring:** Automated apron density tracking allows civil aviation authorities to monitor tarmac congestion and unauthorized aircraft movements without manual photo-interpretation.