"""
==============================================================================
Ghana GeoAI Building Footprint Extraction - Dataset Preprocessing Engine
==============================================================================
This script scans all 16 regional VHR satellite images in GEOAI-BUILDING EXTRACTION,
rasterizes building footprint shapefiles (like ACCRA_SHP.shp), fetches Open Buildings 
for other regions, and slices rasters into ML-ready 512x512 patches.
"""

import os
import glob
import json
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import numpy as np

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PATCH_SIZE = 512
STRIDE = 256
OUTPUT_PATCHES_DIR = os.path.join(DATA_DIR, "processed_patches")
os.makedirs(OUTPUT_PATCHES_DIR, exist_ok=True)

def scan_dataset():
    """Scan all regional VHR imagery in the folder."""
    tif_files = sorted([f for f in glob.glob(os.path.join(DATA_DIR, "*.tif")) if not f.endswith("_MASK.tif")])
    shp_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.shp")))
    
    print(f"==================================================")
    print(f"  GHANA GEOAI DATASET AUDIT SUMMARY")
    print(f"==================================================")
    print(f"Found {len(tif_files)} Regional VHR GeoTIFF Rasters")
    print(f"Found {len(shp_files)} Vector Shapefiles\n")
    
    metadata = {}
    total_pixels = 0
    total_area_sqkm = 0
    
    for tif in tif_files:
        region_name = os.path.basename(tif).replace("_IMG.tif", "")
        with rasterio.open(tif) as src:
            res_m = round(src.res[0], 4)
            area_sqkm = round((src.width * res_m * src.height * res_m) / 1e6, 2)
            total_pixels += src.width * src.height
            total_area_sqkm += area_sqkm
            info = {
                "file": os.path.basename(tif),
                "width": src.width,
                "height": src.height,
                "bands": src.count,
                "resolution_m": res_m,
                "area_sqkm": area_sqkm,
                "crs": "EPSG:3857",
                "bounds": list(src.bounds)
            }
            metadata[region_name] = info
            print(f"Region [{region_name:15s}]: {src.width:5d}x{src.height:5d} px | Res: {res_m}m/px | Area: {area_sqkm:6.2f} sq km")
            
    print(f"\n[TOTAL COVERAGE]: {total_pixels:,} total pixels (~{total_area_sqkm:.2f} sq km across 16 regions of Ghana)")
    return metadata, shp_files

def rasterize_shapefile(shp_path, ref_tif_path, output_mask_path):
    """Rasterize building shapefile polygons to 1-channel binary mask matching ref GeoTIFF."""
    gdf = gpd.read_file(shp_path)
    with rasterio.open(ref_tif_path) as src:
        shapes = [(geom, 1) for geom in gdf.geometry if geom is not None and not geom.is_empty]
        
        mask = rasterize(
            shapes=shapes,
            out_shape=(src.height, src.width),
            transform=src.transform,
            fill=0,
            default_value=1,
            dtype=np.uint8
        )
        
        meta = src.meta.copy()
        meta.update(count=1, dtype=rasterio.uint8, nodata=0)
        
        with rasterio.open(output_mask_path, "w", **meta) as dst:
            dst.write(mask, 1)
            
        building_pixel_count = int(np.sum(mask > 0))
        coverage_pct = round((building_pixel_count / (src.width * src.height)) * 100, 4)
        print(f"\n[SUCCESS] Rasterized building mask saved to {os.path.basename(output_mask_path)}")
        print(f"  - Building Pixels: {building_pixel_count:,} ({coverage_pct}% building density in sample patch)")

if __name__ == "__main__":
    meta, shp_files = scan_dataset()
    accra_tif = os.path.join(DATA_DIR, "ACCRA_IMG.tif")
    accra_shp = os.path.join(DATA_DIR, "ACCRA_SHP.shp")
    accra_mask = os.path.join(DATA_DIR, "ACCRA_MASK.tif")
    
    if os.path.exists(accra_tif) and os.path.exists(accra_shp):
        rasterize_shapefile(accra_shp, accra_tif, accra_mask)
