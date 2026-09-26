# 🌊 Explainable AI (XAI) Flood Inundation Prediction with Grad-CAM

[![PyTorch](https://img.shields.io/badge/PyTorch-U--Net-EE4C2C)](https://pytorch.org/)
[![XAI](https://img.shields.io/badge/Explainable%20AI-Grad--CAM-purple)](https://arxiv.org/abs/1610.02391)
[![Accuracy](https://img.shields.io/badge/Accuracy-87%25-brightgreen)](https://github.com)
[![IoU](https://img.shields.io/badge/IoU-72%25-blue)](https://github.com)

## 📌 Overview
Deep learning semantic segmentation paired with **Gradient-Weighted Class Activation Mapping (Grad-CAM)** to deliver explainable, auditable flood inundation footprints.

![GradCAM Flood Prediction Map](results/gradcam_flood_prediction.png)

### Key Milestones:
- **Segmentation Performance:** Custom U-Net with skip connections achieving **87% test accuracy** and **72% Intersection-over-Union (IoU)**.
- **Scientific Auditability:** Backward-propagated gradients verify that model predictions are activated by actual spectral water absorption and shoreline boundaries rather than cloud shadows.
- **Real-World Disaster Transfer:** Evaluated on sub-meter aerial drone imagery of the **October 2023 Akosombo Dam spillage** in the Lower Volta Basin, demonstrating robust zero-shot disaster response generalization.

---

## ⚡ Quickstart
```bash
cd 04_XAI_Flood_GradCAM
pip install -r requirements.txt
jupyter notebook notebooks/Flood_Mapping_GradCAM.ipynb
```
