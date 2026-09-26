# 🧊 FrostWatch: Arctic Retrogressive Thaw Slump Instance Segmentation

[![Kaggle Leaderboard](https://img.shields.io/badge/Kaggle-Rank%20%231%20Global-gold?logo=kaggle&logoColor=white)](https://kaggle.com)
[![Average Precision](https://img.shields.io/badge/AP-16.24-brightgreen)](https://kaggle.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![SMP](https://img.shields.io/badge/SMP-UNet%2B%2B%20%7C%20DeepLabV3%2B%20%7C%20MAnet-blue)](https://github.com/qubvel/segmentation_models.pytorch)

## 📌 Overview
FrostWatch is a state-of-the-art **3-arm mean-fusion deep learning ensemble** designed to detect and segment Retrogressive Thaw Slumps (RTS) in Arctic permafrost terrain from high-resolution satellite imagery. It achieved **Rank #1 on the competition leaderboard (16.24 AP)** on Kaggle 2×T4 GPU infrastructure.

---

## 🏗️ 3-Arm Mean-Fusion Architecture

| Model Arm | Decoder Architecture | Backbone Encoder | Specific Spatial Role |
|---|---|---|---|
| **Arm 1** | **UNet++** | SE-ResNeXt50 (32x4d) | Nested dense skip connections preserving high-frequency boundary edges |
| **Arm 2** | **DeepLabV3+** | EfficientNet-B5 | Atrous Spatial Pyramid Pooling (ASPP) for multi-scale spatial receptive fields |
| **Arm 3** | **MAnet** | MiT-B5 (Transformer) | Multi-scale attention capturing long-range contextual spatial relationships |

$$\hat{Y}_{	ext{ensemble}} = rac{1}{3} \Big[ \sigma(f_{	ext{UNet++}}(X)) + \sigma(f_{	ext{DeepLabV3+}}(X)) + \sigma(f_{	ext{MAnet}}(X)) \Big]$$

---

## 🔬 13-Channel Multi-Modal Tensor Engineering
Raw spectral bands alone struggle to differentiate mud scars from active permafrost slump headwalls. We engineered **13-channel input tensors** at 512×512 resolution:

$$\mathbf{X} \in \mathbb{R}^{13 	imes 512 	imes 512} = \Big[ B_1, \dots, B_8, \;
abla_x
abla_y 	ext{ (Sobel Slope)}, \;
abla^2 	ext{ (Laplacian Curvature)}, \;	ext{IOR}, \;	ext{NDVI} 	imes 	ext{Slope}, \;	ext{Elevation} \Big]$$

---

## 🏆 Leaderboard Benchmark
- **Competition Standing:** **Rank #1 Globally**
- **Overall AP:** **16.24**
- **Small Slump AP ($AP_{	ext{small}}$):** Boosted from $3.33 	o 5.0+$ using Area-Attenuated Focal+Dice loss.
- **Boundary Moat ($AP_{75}$):** Maintained at **9.65** boundary precision.
