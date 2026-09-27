# Automated Feature Extraction with Foundation Models: SAMGeo & LangSAM
## Case Study: Zero-Shot Campus Infrastructure & Aviation Intelligence in Ghana

[![Segment Anything](https://img.shields.io/badge/Meta%20AI-Segment%20Anything-blue?logo=meta)](https://segment-anything.com/)
[![SAMGeo](https://img.shields.io/badge/SAMGeo-Segment%20Geospatial-green)](https://samgeo.gishub.org/)
[![LangSAM](https://img.shields.io/badge/LangSAM-Grounding%20DINO%20%2B%20SAM-orange)](https://github.com/luca-medeiros/lang-segment-anything)

### 1. Introduction: The Spatial Logic of Foundation Models in Remote Sensing
In classical Earth Observation, extracting structural built features requires laborious manual polygon digitization or supervised training of CNNs on thousands of manually annotated tiles. This project implements **Geospatial Foundation Models (SAMGeo & LangSAM)**, adapting Meta AI's **Segment Anything Model (SAM)** and Vision Transformer (ViT) backbones to remote sensing imagery.

By utilizing **zero-shot learning** and **natural language prompt engineering**, we eliminate the need for task-specific training data while maintaining sub-meter boundary precision across complex architectural and vehicular targets.

---

### 2. Methodological Pipeline

#### 2.1 Promptable Vision Transformer Inference (SAMGeo)
- **The Process**: We ingest sub-meter satellite/aerial imagery into pre-trained Vision Transformer backbones (`vit_h`, `vit_l`, `vit_b`). Image embeddings are computed once, and spatial masks are decoded in real-time.
- **The Essence**: ViT self-attention heads capture global spatial context and high-frequency structural edges simultaneously. This allows SAMGeo to delineate complex building footprints without edge degradation.

#### 2.2 Dual-Branch Natural Language Grounding (LangSAM)
- **The Process**: We pair **Grounding DINO** (open-vocabulary object detector) with **SAM** (segmentation engine). A natural language text prompt (e.g., `"Airplanes"`) is passed to detect bounding boxes, which are instantly fed to SAM as geometric prompt coordinates.
- **The Essence**: Decouples semantic identification from pixel-level boundary refinement. Grounding DINO handles the open-vocabulary localization, while SAM computes the high-precision instance mask.

---

### 3. Scenario Analysis: Empirical Insights

#### Scenario 1: Anchor Academic Landmark (Sam Jonah Library & UCC Campus)
- **Purpose**: Zero-shot structural footprint segmentation of primary institutional complexes at the University of Cape Coast without fine-tuning.

<p align="center">
  <img src="https://github.com/user-attachments/assets/9a721048-0a90-44fd-a5e2-8273ee73c4f7" width="450" alt="Raw Satellite Image">
  <img src="https://github.com/user-attachments/assets/32aaf4d0-b315-4df0-ab91-298e0b976bbf" width="450" alt="Segmented Output">
  <br>
  <em>Figure 1: Raw sub-meter aerial imagery (left) versus SAMGeo zero-shot structural segmentation (right).</em>
</p>

- **Insight**: Demonstrates remarkable **zero-shot boundary delineation**. The model cleanly isolates the non-rectangular footprint of the Sam Jonah Library and adjacent lecture halls, distinguishing impervious concrete roof structures from surrounding ornamental canopy without manual supervision.

#### Scenario 2: High-Density Strategic Asset (Kotoka International Airport Aviation Intelligence)
- **Purpose**: Automated localization and instance segmentation of commercial airliners parked on the tarmac aprons of Accra's international airport.

<p align="center">
  <img src="https://github.com/user-attachments/assets/0ddb8abc-c594-4b73-b6ed-f0e9c92dfc21" width="420" alt="Bounding Box Localization">
  <img src="https://github.com/user-attachments/assets/907a3c5f-c38f-4cd9-9f46-7203f5429f78" width="420" alt="Instance Segmentation Mask">
  <br>
  <em>Figure 2: Grounding DINO text-prompted bounding box localization (left) and SAM instance segmentation refinement (right).</em>
</p>

- **Insight**: Validates the **two-stage detection-segmentation pipeline**. Text prompt `"Airplanes"` successfully guides Grounding DINO to detect multiple aircraft regardless of orientation or livery. SAM subsequently isolates wings, fuselage, and tailfins from high-reflectance tarmac surfaces with pixel-perfect accuracy.

---

### 4. Operational & Planning Implications
Geospatial foundation models fundamentally change the economics of spatial intelligence:
1. **Rapid Disaster Damage Mapping:** Zero-shot building extraction enables emergency response teams to quantify structural collapses within minutes of new satellite acquisition.
2. **Aviation & Logistics Monitoring:** Automated apron density tracking allows civil aviation authorities to monitor tarmac congestion and unauthorized aircraft movements without manual photo-interpretation.
