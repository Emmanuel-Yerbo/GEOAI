# 🏢 Nationwide Building Footprint Extraction with SegFormer & Foundation Models

[![TorchGeo](https://img.shields.io/badge/TorchGeo-Spatial%20Samplers-green)](https://github.com/microsoft/torchgeo)
[![SegFormer](https://img.shields.io/badge/HuggingFace-SegFormer--B3-yellow)](https://huggingface.co/)
[![ONNX](https://img.shields.io/badge/Inference-ONNX%20Runtime-blue)](https://onnxruntime.ai/)

## 📌 Overview
An end-to-end deep learning segmentation and vectorization pipeline extracting building footprints across all 16 administrative regions of Ghana from 30cm Very High Resolution (VHR) satellite imagery.

### Engineering Highlights:
- **Model Benchmarking:** Fine-tuned **SegFormer-B3** (Mix Transformer encoder), **DINOv3** foundation models, and U-Net baselines in PyTorch Lightning.
- **TorchGeo Integration:** Employs `torchgeo.datasets.RasterDataset` with `GridGeoSampler` and `RandomGeoSampler` for seamless geospatial chip sampling without boundary edge distortion.
- **Geometric Regularization & Vectorization:** Post-processes raw segmentation probability masks into crisp, orthogonal right-angled building polygons via Douglas-Peucker simplification and minimum rotated bounding rectangles.
- **ONNX Deployment:** Models exported to ONNX runtime for ultra-fast production inference.
