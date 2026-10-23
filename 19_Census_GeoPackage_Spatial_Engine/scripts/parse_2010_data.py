import requests
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")

# 1. Load 16 region names from regional shapefile
print("Loading official region list from shapefile...")
gdf_regions = gpd.read_file(BASE / "shapefiles" / "extracted_shp" / "gha_admin1.shp")
regions_16 = [r.strip().lower() for r in gdf_regions["adm1_name"].unique()]
print(f"Regions (16): {regions_16}")

# 2. Fetch the 2010 StatsBank table
url = "https://statsbank.statsghana.gov.gh/api/v1/en/PHC2010/Population/ethnic_table.px"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
payload = {
  "query": [
    {"code": "Ethnicity", "selection": {"filter": "item", "values": ["Total"]}},
    {"code": "Education", "selection": {"filter": "item", "values": ["Total"]}},
    {"code": "Locality", "selection": {"filter": "item", "values": ["All Locality Types"]}},
    {"code": "Sex", "selection": {"filter": "item", "values": ["Both sexes"]}},
    {"code": "Age", "selection": {"filter": "item", "values": ["All ages"]}}
  ],
  "response": {"format": "json"}
}

print("\nQuerying 2010 census table...")
res = requests.post(url, json=payload, headers=headers)
if res.ok:
    data = res.json()
    rows = []
    for item in data.get("data", []):
        key = item.get("key", [])
        value = item.get("values", [None])[0]
        geo = key[3]
        rows.append({"geographic_area": geo, "pop_2010": int(value) if value is not None else None})
        
    df = pd.DataFrame(rows)
    df["name_clean"] = df["geographic_area"].str.strip()
    # Normalize naming mismatch: 'North East' -> 'Northern East'
    df.loc[df["name_clean"] == "North East", "name_clean"] = "Northern East"
    df["name_lower"] = df["name_clean"].str.lower()
    
    # 3. Classify rows
    df_national = df[df["name_lower"] == "ghana"]
    df_regions = df[df["name_lower"].isin(regions_16) | (df["name_lower"] == "brong ahafo")]
    df_districts = df[~df["name_lower"].isin(regions_16) & (df["name_lower"] != "brong ahafo") & (df["name_lower"] != "ghana")]
    
    print(f"\nNational rows: {len(df_national)}")
    print(f"Regional rows: {len(df_regions)} (expected 16)")
    print(f"District rows: {len(df_districts)}")
    
    # Save the parsed data to CSV
    df_regions[["geographic_area", "pop_2010", "name_clean"]].to_csv(BASE / "data" / "ghana_regions_pop_2010.csv", index=False)
    df_districts[["geographic_area", "pop_2010", "name_clean"]].to_csv(BASE / "data" / "ghana_districts_pop_2010.csv", index=False)
    print("\nSaved corrected CSVs under data/")
else:
    print(f"Failed: {res.status_code}")
