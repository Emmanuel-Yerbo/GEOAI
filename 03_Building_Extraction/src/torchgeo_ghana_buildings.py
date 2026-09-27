"""
==============================================================================
Ghana GeoAI Building Footprint Extraction - TorchGeo & Lightning Pipeline
==============================================================================
This module implements custom TorchGeo RasterDatasets, spatial samplers,
and a PyTorch Lightning model task for extracting building footprints from
the 16-region 30cm VHR Ghana satellite imagery dataset.
"""

import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchgeo.datasets import RasterDataset, stack_samples
from torchgeo.samplers import RandomGeoSampler, GridGeoSampler
from torchgeo.trainers import SemanticSegmentationTask
import lightning.pytorch as pl
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. TorchGeo Custom Imagery RasterDataset (30cm 3-band RGB VHR)
class GhanaVHRImageryDataset(RasterDataset):
    """
    TorchGeo loader for 30cm Very High Resolution (VHR) RGB imagery over Ghana.
    Covers Accra, Kumasi, Central, Western, Northern, and 11 other regions.
    """
    filename_glob = "*_IMG.tif"
    is_image = True
    all_bands = ["R", "G", "B"]
    rgb_bands = ["R", "G", "B"]

# 2. TorchGeo Custom Building Mask RasterDataset
class GhanaBuildingMaskDataset(RasterDataset):
    """
    TorchGeo loader for binary building masks (0=background, 1=building footprint).
    """
    filename_glob = "*_MASK.tif"
    is_image = False

# 3. Pipeline Factory
def get_ghana_building_dataloaders(data_dir=DATA_DIR, patch_size=512, batch_size=4, num_workers=2):
    """
    Creates TorchGeo IntersectionDataset and returns DataLoader with RandomGeoSampler.
    """
    imagery_ds = GhanaVHRImageryDataset(paths=data_dir)
    mask_ds    = GhanaBuildingMaskDataset(paths=data_dir)
    
    # IntersectionDataset aligns spatial extents automatically
    combined_dataset = imagery_ds & mask_ds
    
    print(f"[TorchGeo] Dataset Initialized successfully!")
    print(f"  - CRS: {combined_dataset.crs}")
    print(f"  - Bounds: {combined_dataset.bounds}")
    
    # Spatial sampler extracts 512x512 pixel patches (~153m x 153m per patch)
    train_sampler = RandomGeoSampler(combined_dataset, size=patch_size, length=100)
    
    train_loader = DataLoader(
        combined_dataset,
        sampler=train_sampler,
        batch_size=batch_size,
        collate_fn=stack_samples,
        num_workers=num_workers
    )
    
    return combined_dataset, train_loader

# 4. PyTorch Lightning Model Task Setup
def create_building_extraction_model(learning_rate=1e-4):
    """
    Builds a SemanticSegmentationTask using a U-Net architecture with
    Pre-trained ResNet-50 backbone for 3-channel VHR building footprint extraction.
    """
    task = SemanticSegmentationTask(
        model="unet",
        backbone="resnet50",
        weights="imagenet",       # ImageNet weights work best for 3-band RGB VHR imagery
        in_channels=3,            # RGB input
        num_classes=2,            # 0: Non-building, 1: Building
        lr=learning_rate,
        loss="dice",              # Dice Loss maximizes boundary IoU for buildings
    )
    return task

if __name__ == "__main__":
    print("Testing TorchGeo Ghana Building Dataset Pipeline...")
    try:
        ds, loader = get_ghana_building_dataloaders(patch_size=512, batch_size=2)
        model_task = create_building_extraction_model()
        print("Model Task created successfully!")
        
        # Test iteration
        for batch in loader:
            imgs = batch["image"]  # [B, 3, 512, 512]
            masks = batch["mask"]  # [B, 1, 512, 512]
            print(f"Sample Batch Image Tensor Shape: {imgs.shape}")
            print(f"Sample Batch Mask Tensor Shape:  {masks.shape}")
            break
    except Exception as e:
        print(f"Pipeline verification note: {e}")
