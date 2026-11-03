"""
Windowed Block-Wise Raster Inference Engine for Spectral Neural Networks
Emmanuel Yerbo | GeoAI Baseline Engine
"""

import os
import argparse
import numpy as np
import rasterio
from rasterio.windows import Window
import torch

from model import SpectralMLP


def predict_geotiff_windowed(
    input_tif: str,
    output_tif: str,
    model_path: str = None,
    block_size: int = 1024,
    device: str = "cpu"
):
    """
    Executes memory-safe chunked inference across large multi-spectral GeoTIFFs.
    Streams pixel blocks without loading entire gigabyte rasters into memory.
    """
    if not os.path.exists(input_tif):
        print(f"Input raster not found: {input_tif}. Aborting raster inference.")
        return

    with rasterio.open(input_tif) as src:
        profile = src.profile.copy()
        profile.update({
            "count": 1,
            "dtype": "uint8",
            "nodata": 0,
            "compress": "lzw"
        })

        in_channels = src.count
        height, width = src.height, src.width
        print(f"Processing raster: {width}x{height} pixels, {in_channels} bands")

        # Load or initialize model
        model = SpectralMLP(in_features=in_channels, hidden_dims=[64, 128, 64, 32], num_classes=4).to(device)
        if model_path and os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()

        with rasterio.open(output_tif, "w", **profile) as dst:
            for row in range(0, height, block_size):
                h = min(block_size, height - row)
                for col in range(0, width, block_size):
                    w = min(block_size, width - col)
                    window = Window(col, row, w, h)

                    # Read window data: (bands, h, w)
                    data = src.read(window=window)
                    # Reshape to (h * w, bands)
                    pixels = data.reshape(in_channels, -1).T
                    pixels = np.nan_to_num(pixels, nan=0.0)

                    # Model forward pass
                    with torch.no_grad():
                        t_pixels = torch.tensor(pixels, dtype=torch.float32).to(device)
                        logits = model(t_pixels)
                        # Add 1 so classes are 1..4 (0 is nodata)
                        preds = torch.argmax(logits, dim=1).cpu().numpy().astype(np.uint8) + 1

                    out_block = preds.reshape(h, w)
                    dst.write(out_block, 1, window=window)

        print(f"Classification successfully saved to: {output_tif}")


def main():
    parser = argparse.ArgumentParser(description="Predict LULC map from GeoTIFF")
    parser.add_argument("--input", type=str, required=True, help="Input multi-spectral GeoTIFF")
    parser.add_argument("--output", type=str, required=True, help="Output classified GeoTIFF")
    parser.add_argument("--model", type=str, default=None, help="Trained model weights (.pt)")
    parser.add_argument("--block-size", type=int, default=1024, help="Block window size")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    predict_geotiff_windowed(args.input, args.output, args.model, args.block_size, device)


if __name__ == "__main__":
    main()
