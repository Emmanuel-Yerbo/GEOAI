import requests
import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
SHP_DIR = BASE_DIR / "shapefiles"
DATA_DIR = BASE_DIR / "data"

SHP_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

def fetch_package_resources(package_id):
    url = f"https://data.humdata.org/api/3/action/package_show?id={package_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("result", {}).get("resources", [])
    else:
        print(f"Error fetching package {package_id}: Status {response.status_code}")
        return []

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Finished downloading {dest_path.name}")
    else:
        print(f"Failed to download {url}: Status {response.status_code}")

# Get boundary files
print("Fetching boundary resources...")
boundary_resources = fetch_package_resources("cod-ab-gha")
for res in boundary_resources:
    name = res.get("name", "")
    url = res.get("url", "")
    fmt = res.get("format", "").upper()
    print(f"Found Boundary Resource: {name} ({fmt})")
    
    # We want SHP (Shapefile) and/or GeoJSON
    if "SHP" in fmt or "SHAPEFILE" in name.upper() or "ZIP" in fmt:
        if "shp" in name.lower() or "shp" in url.lower():
            dest = SHP_DIR / "gha_boundaries_shp.zip"
            if not dest.exists():
                download_file(url, dest)
    elif "GEOJSON" in fmt:
        dest = SHP_DIR / f"{name}.geojson"
        if not dest.exists():
            download_file(url, dest)

# Get population statistics files
print("\nFetching population resources...")
pop_resources = fetch_package_resources("cod-ps-gha")
for res in pop_resources:
    name = res.get("name", "")
    url = res.get("url", "")
    fmt = res.get("format", "").upper()
    print(f"Found Population Resource: {name} ({fmt})")
    
    # We want CSV or XLSX
    if fmt in ["CSV", "XLSX"]:
        # Normalize filename
        clean_name = name.replace(" ", "_").replace("/", "_")
        if not clean_name.endswith(fmt.lower()):
            clean_name += f".{fmt.lower()}"
        dest = DATA_DIR / clean_name
        if not dest.exists():
            download_file(url, dest)
