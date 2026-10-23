import geopandas as gpd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
GPKG_PATH = BASE_DIR / "output" / "ghana_census_2021.gpkg"
SHP_OUT_DIR = BASE_DIR / "output" / "shapefiles"
SHP_OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load regions layer
print("Loading regional demographics...")
gdf_regions = gpd.read_file(GPKG_PATH, layer="regions_demographics")

# Calculate indicators and rename columns for clarity
gdf_regions["pop_2021"] = gdf_regions["t_tl"]
gdf_regions["growth_abs"] = gdf_regions["pop_2021"] - gdf_regions["pop_2010"]
gdf_regions["growth_pct"] = (gdf_regions["growth_abs"] / gdf_regions["pop_2010"]) * 100

# Drop the original 't_tl' to avoid duplicate columns
gdf_regions = gdf_regions.drop(columns=["t_tl"])

# 2. Load districts layer
print("Loading district demographics...")
gdf_districts = gpd.read_file(GPKG_PATH, layer="districts_demographics")

# Calculate indicators and rename columns for clarity
gdf_districts["pop_2021"] = gdf_districts["t_tl"]
gdf_districts["growth_abs"] = gdf_districts["pop_2021"] - gdf_districts["pop_2010"]
gdf_districts["growth_pct"] = np.where(gdf_districts["pop_2010"] > 0, (gdf_districts["growth_abs"] / gdf_districts["pop_2010"]) * 100, 0)

# Drop the original 't_tl'
gdf_districts = gdf_districts.drop(columns=["t_tl"])

# 3. Export to ESRI Shapefile
# Note: Shapefiles truncate column names to 10 characters.
# Let's clean the column names to avoid duplication warnings or clashes where possible.
def clean_columns_for_shapefile(gdf):
    # Rename long columns manually to ensure they don't clash or truncate cryptically
    rename_dict = {}
    for col in gdf.columns:
        if len(col) > 10:
            # Check if it starts with f_ or m_ or t_ and contains ages
            # Example: f_15_19 (7 chars) is fine.
            # Example: area_sqkm (9 chars) is fine.
            # Example: growth_rate_clipped -> gr_clipped
            if col == "growth_rate_clipped":
                rename_dict[col] = "gr_clipped"
    return gdf.rename(columns=rename_dict)

print("\nCleaning columns...")
gdf_regions_shp = clean_columns_for_shapefile(gdf_regions)
gdf_districts_shp = clean_columns_for_shapefile(gdf_districts)

print("\nExporting regions shapefile...")
regions_shp_path = SHP_OUT_DIR / "ghana_regions_census.shp"
gdf_regions_shp.to_file(regions_shp_path, driver="ESRI Shapefile")
print(f"Regions shapefile successfully saved to: {regions_shp_path}")

print("\nExporting districts shapefile...")
districts_shp_path = SHP_OUT_DIR / "ghana_districts_census.shp"
gdf_districts_shp.to_file(districts_shp_path, driver="ESRI Shapefile")
print(f"Districts shapefile successfully saved to: {districts_shp_path}")
