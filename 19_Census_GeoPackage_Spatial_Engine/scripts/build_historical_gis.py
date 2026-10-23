import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
GPKG_PATH = BASE_DIR / "output" / "ghana_census_2021.gpkg"
DATA_DIR = BASE_DIR / "data"

# 1. Load the 2010 data we extracted
print("Loading 2010 census CSVs...")
df_pop_2010_adm1 = pd.read_csv(DATA_DIR / "ghana_regions_pop_2010.csv")
df_pop_2010_adm2 = pd.read_csv(DATA_DIR / "ghana_districts_pop_2010.csv")

# 2. Load the 2021 pre-split mapping from the Excel file
print("Loading 2021 Excel mapping...")
excel_path = DATA_DIR / "gha_admpop_2021.xlsx"
df_ps = pd.read_excel(excel_path, sheet_name="gha_admpop_adm2PS_2021")

# Clean up names in mapping
df_ps["ADM2_EN_PS_clean"] = df_ps["ADM2_EN_PS"].str.strip()
df_ps["ADM2_PCODE_clean"] = df_ps["ADM2_PCODE"].str.strip().str.upper()

# Clean up 2010 district names
df_pop_2010_adm2["name_clean"] = df_pop_2010_adm2["name_clean"].str.strip()

# 3. Map 2010 districts to 2021 P-codes
print("Mapping 2010 districts to 2021 standard P-codes...")
df_pop_2010_mapped = df_pop_2010_adm2.merge(
    df_ps[["ADM2_EN_PS_clean", "ADM2_PCODE_clean"]],
    left_on="name_clean",
    right_on="ADM2_EN_PS_clean",
    how="left"
)

# Check for missing mappings
missing_mappings = df_pop_2010_mapped[df_pop_2010_mapped["ADM2_PCODE_clean"].isnull()]
if len(missing_mappings) > 0:
    print(f"Warning: {len(missing_mappings)} districts could not be mapped to 2021 P-codes:")
    print(missing_mappings["name_clean"].unique())
else:
    print("All 2010 districts mapped successfully!")

# 4. Group by 2021 standard P-code and sum the 2010 population
# (this aggregates sub-metropolitan/municipal divisions into their standard parent boundaries)
print("Aggregating 2010 populations by 2021 district P-codes...")
df_pop_2010_adm2_grouped = df_pop_2010_mapped.groupby("ADM2_PCODE_clean")["pop_2010"].sum().reset_index()
print(f"Aggregated 2010 data to {len(df_pop_2010_adm2_grouped)} unique districts")

# 5. Load the GeoPackage layers
print("\nLoading GeoPackage layers...")
gdf_regions = gpd.read_file(GPKG_PATH, layer="regions_demographics")
gdf_districts = gpd.read_file(GPKG_PATH, layer="districts_demographics")

# Make the script idempotent by dropping existing 'pop_2010' columns if they exist
if "pop_2010" in gdf_districts.columns:
    gdf_districts = gdf_districts.drop(columns=["pop_2010"])
if "pop_2010" in gdf_regions.columns:
    gdf_regions = gdf_regions.drop(columns=["pop_2010"])

print(f"Loaded regions: {gdf_regions.shape} features")
print(f"Loaded districts: {gdf_districts.shape} features")

# 6. Merge 2010 populations into GeoPackage layers
# Standardize P-code column names to join
gdf_districts["join_pcode"] = gdf_districts["adm2_pcode"].str.strip().str.upper()
df_pop_2010_adm2_grouped["join_pcode"] = df_pop_2010_adm2_grouped["ADM2_PCODE_clean"]

# Join 2010 population into standard districts layer
print("\nJoining 2010 district population to shapefile...")
gdf_districts_updated = gdf_districts.merge(
    df_pop_2010_adm2_grouped[["join_pcode", "pop_2010"]],
    on="join_pcode",
    how="left"
)
gdf_districts_updated = gdf_districts_updated.drop(columns=["join_pcode"])

# Check for any districts with missing 2010 population
missing_pop_2010 = gdf_districts_updated[gdf_districts_updated["pop_2010"].isnull()]
if len(missing_pop_2010) > 0:
    print(f"Warning: {len(missing_pop_2010)} districts have missing 2010 population!")
    print(missing_pop_2010[["adm2_name", "adm2_pcode"]])
else:
    print("All districts successfully joined with 2010 population!")

# 7. Merge 2010 population into regions layer
df_pop_2010_adm1["name_clean"] = df_pop_2010_adm1["name_clean"].str.strip().str.lower()
gdf_regions["name_lower"] = gdf_regions["adm1_name"].str.strip().str.lower()

print("\nJoining 2010 regional population to shapefile...")
gdf_regions_updated = gdf_regions.merge(
    df_pop_2010_adm1[["name_clean", "pop_2010"]],
    left_on="name_lower",
    right_on="name_clean",
    how="left"
)
gdf_regions_updated = gdf_regions_updated.drop(columns=["name_lower", "name_clean"])

missing_reg_2010 = gdf_regions_updated[gdf_regions_updated["pop_2010"].isnull()]
if len(missing_reg_2010) > 0:
    print(f"Warning: {len(missing_reg_2010)} regions have missing 2010 population!")
    print(missing_reg_2010[["adm1_name", "adm1_pcode"]])
else:
    print("All regions successfully joined with 2010 population!")

# 8. Save updated layers back to GeoPackage
print(f"\nWriting updated layers back to: {GPKG_PATH}...")
gdf_regions_updated.to_file(GPKG_PATH, layer="regions_demographics", driver="GPKG")
gdf_districts_updated.to_file(GPKG_PATH, layer="districts_demographics", driver="GPKG")

print("GIS Database updated successfully with 2010 census populations!")
