import geopandas as gpd
from pathlib import Path

EXTRACT_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA\shapefiles\extracted_shp")
shp_files = list(EXTRACT_DIR.glob("**/*.shp"))

print(f"Found {len(shp_files)} shapefiles:")
for sf in shp_files:
    print(f"\nFile: {sf.name}")
    try:
        gdf = gpd.read_file(sf)
        print(f"  Shape: {gdf.shape}")
        print(f"  Columns: {gdf.columns.tolist()}")
        # Check unique region names
        for col in gdf.columns:
            if "ADM1" in col and "EN" in col:
                print(f"  Unique ADM1 Names ({len(gdf[col].unique())}): {gdf[col].unique().tolist()[:10]}")
            if "ADM2" in col and "EN" in col:
                print(f"  Unique ADM2 Names ({len(gdf[col].unique())}): {gdf[col].unique().tolist()[:10]}")
    except Exception as e:
        print(f"  Error reading: {e}")
