import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
SHP_EXTRACT_DIR = BASE_DIR / "shapefiles" / "extracted_shp"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Paths
adm1_shp_path = SHP_EXTRACT_DIR / "gha_admin1.shp"
adm2_shp_path = SHP_EXTRACT_DIR / "gha_admin2.shp"
excel_path = DATA_DIR / "gha_admpop_2021.xlsx"

print("Loading shapefiles...")
# Load Shapefiles
gdf_adm1 = gpd.read_file(adm1_shp_path)
gdf_adm2 = gpd.read_file(adm2_shp_path)

print(f"Loaded ADM1 Shapefile: {gdf_adm1.shape} features")
print(f"Loaded ADM2 Shapefile: {gdf_adm2.shape} features")

print("\nLoading Excel Sheets...")
# Load Excel Sheets
xl = pd.ExcelFile(excel_path)
df_pop_adm1 = xl.parse("gha_admpop_adm1_2021")
df_pop_adm2 = xl.parse("gha_admpop_adm2_2021")

print(f"Loaded ADM1 Demographics: {df_pop_adm1.shape} rows")
print(f"Loaded ADM2 Demographics: {df_pop_adm2.shape} rows")

# 2. Drop redundant metadata columns from Excel dataframes to avoid SQLite duplicate column errors
# (since SQLite is case-insensitive, e.g. adm0_pcode and ADM0_PCODE conflict)
cols_to_drop_adm1 = ["year", "ISO3", "ADM0_EN", "ADM0_PCODE", "ADM1_EN"]
# Keep ADM1_PCODE for the join, then drop or rename it
df_pop_adm1_clean = df_pop_adm1.drop(columns=[c for c in cols_to_drop_adm1 if c in df_pop_adm1.columns])

cols_to_drop_adm2 = ["year", "ISO3", "ADM0_EN", "ADM0_PCODE", "ADM1_EN", "ADM1_PCODE", "ADM2_EN"]
# Keep ADM2_PCODE for the join, then drop or rename it
df_pop_adm2_clean = df_pop_adm2.drop(columns=[c for c in cols_to_drop_adm2 if c in df_pop_adm2.columns])

# 3. Standardize Join Keys
gdf_adm1["join_pcode"] = gdf_adm1["adm1_pcode"].str.strip().str.upper()
df_pop_adm1_clean["join_pcode"] = df_pop_adm1_clean["ADM1_PCODE"].str.strip().str.upper()
df_pop_adm1_clean = df_pop_adm1_clean.drop(columns=["ADM1_PCODE"])

gdf_adm2["join_pcode"] = gdf_adm2["adm2_pcode"].str.strip().str.upper()
df_pop_adm2_clean["join_pcode"] = df_pop_adm2_clean["ADM2_PCODE"].str.strip().str.upper()
df_pop_adm2_clean = df_pop_adm2_clean.drop(columns=["ADM2_PCODE"])

# 4. Perform Joins
print("\nPerforming spatial joins...")
joined_adm1 = gdf_adm1.merge(df_pop_adm1_clean, on="join_pcode", how="left")
joined_adm2 = gdf_adm2.merge(df_pop_adm2_clean, on="join_pcode", how="left")

# Clean up temporary join keys
joined_adm1 = joined_adm1.drop(columns=["join_pcode"])
joined_adm2 = joined_adm2.drop(columns=["join_pcode"])

# Ensure all column names are lowercase to match GIS best practices
joined_adm1.columns = [c.lower() for c in joined_adm1.columns]
joined_adm2.columns = [c.lower() for c in joined_adm2.columns]

print(f"Joined ADM1: {joined_adm1.shape} features")
print(f"Joined ADM2: {joined_adm2.shape} features")

# Check for any unjoined regions/districts
unjoined_adm1 = joined_adm1[joined_adm1["t_tl"].isnull()]
unjoined_adm2 = joined_adm2[joined_adm2["t_tl"].isnull()]

if len(unjoined_adm1) > 0:
    print(f"Warning: {len(unjoined_adm1)} ADM1 features failed to join population data!")
    print(unjoined_adm1[["adm1_name", "adm1_pcode"]])
else:
    print("All ADM1 regions joined successfully!")

if len(unjoined_adm2) > 0:
    print(f"Warning: {len(unjoined_adm2)} ADM2 districts failed to join population data!")
    print(unjoined_adm2[["adm2_name", "adm2_pcode"]].head(10))
else:
    print("All ADM2 districts joined successfully!")

# 5. Save to Multi-layer GeoPackage
gpkg_path = OUTPUT_DIR / "ghana_census_2021.gpkg"
print(f"\nSaving layers to GeoPackage: {gpkg_path}...")

# GeoPackage handles multiple layers perfectly
joined_adm1.to_file(gpkg_path, layer="regions_demographics", driver="GPKG")
joined_adm2.to_file(gpkg_path, layer="districts_demographics", driver="GPKG")

print("Saved successfully!")
