import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

BASE_DIR = Path(r"c:\YERBO\Desktop\CODING\POPULATION DATA")
GPKG_PATH = BASE_DIR / "output" / "ghana_census_2021.gpkg"
MAP_DIR = BASE_DIR / "output" / "maps"
MAP_DIR.mkdir(exist_ok=True)

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'

def create_regional_growth_map():
    print("Loading regional demographics layer...")
    gdf = gpd.read_file(GPKG_PATH, layer="regions_demographics")
    
    # Calculate indicators
    # pop_2021 is stored as 't_tl' in the 2021 demographics merge
    gdf["growth_abs"] = gdf["t_tl"] - gdf["pop_2010"]
    gdf["growth_rate"] = (gdf["growth_abs"] / gdf["pop_2010"]) * 100
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    
    # Map 1: Absolute Growth
    ax1 = axes[0]
    gdf.plot(
        column="growth_abs",
        cmap="Blues",
        legend=True,
        edgecolor="black",
        linewidth=0.5,
        ax=ax1,
        legend_kwds={"label": "Absolute Population Growth (Millions)", "orientation": "horizontal", "pad": 0.05}
    )
    # Format labels to millions
    colorbar = ax1.collections[0].colorbar
    if colorbar:
        colorbar.set_ticks(colorbar.get_ticks())
        colorbar.set_ticklabels([f"{x/1e6:.2f}M" for x in colorbar.get_ticks()])
        
    ax1.set_title("Ghana Regions: Absolute Population Growth (2010-2021)", fontsize=16, fontweight='bold')
    ax1.axis("off")
    
    # Map 2: Growth Rate (%)
    ax2 = axes[1]
    gdf.plot(
        column="growth_rate",
        cmap="YlOrRd",
        legend=True,
        edgecolor="black",
        linewidth=0.5,
        ax=ax2,
        legend_kwds={"label": "Percentage Population Growth (%)", "orientation": "horizontal", "pad": 0.05}
    )
    ax2.set_title("Ghana Regions: Percentage Growth Rate (2010-2021)", fontsize=16, fontweight='bold')
    ax2.axis("off")
    
    # Annotate region names
    for idx, row in gdf.iterrows():
        centroid = row['geometry'].centroid
        name = row['adm1_name']
        ax1.annotate(text=name, xy=(centroid.x, centroid.y), xytext=(3, 3), 
                     textcoords="offset points", fontsize=8, color="black", weight="semibold")

    plt.tight_layout()
    map_path = MAP_DIR / "ghana_regional_growth_2010_2021.png"
    plt.savefig(map_path, dpi=300, bbox_inches='tight')
    print(f"Saved regional growth map to {map_path}")
    plt.close()

def create_district_growth_map():
    print("Loading district demographics layer...")
    gdf = gpd.read_file(GPKG_PATH, layer="districts_demographics")
    
    # Calculate indicators
    gdf["growth_abs"] = gdf["t_tl"] - gdf["pop_2010"]
    # Handle division by zero or NaN cases if pop_2010 is zero
    gdf["growth_rate"] = np.where(gdf["pop_2010"] > 0, (gdf["growth_abs"] / gdf["pop_2010"]) * 100, 0)
    
    # Cap outlier growth rates (e.g. from fast developing metropolitan fringes) at 150% for visualization clarity
    gdf["growth_rate_clipped"] = np.clip(gdf["growth_rate"], -50, 150)
    
    fig, axes = plt.subplots(1, 2, figsize=(24, 16))
    
    # Map 1: Absolute Growth
    ax1 = axes[0]
    gdf.plot(
        column="growth_abs",
        cmap="Purples",
        legend=True,
        edgecolor="black",
        linewidth=0.1,
        ax=ax1,
        legend_kwds={"label": "Absolute Growth (People)", "orientation": "horizontal", "pad": 0.05}
    )
    ax1.set_title("Ghana Districts: Absolute Population Growth (2010-2021)", fontsize=16, fontweight='bold')
    ax1.axis("off")
    
    # Map 2: Percentage Growth
    ax2 = axes[1]
    gdf.plot(
        column="growth_rate_clipped",
        cmap="RdYlGn", # Red (negative growth/decline), Yellow (low growth), Green (high growth)
        legend=True,
        edgecolor="black",
        linewidth=0.1,
        ax=ax2,
        legend_kwds={"label": "Percentage Growth (Capped at 150%)", "orientation": "horizontal", "pad": 0.05}
    )
    ax2.set_title("Ghana Districts: Percentage Growth Rate (2010-2021)", fontsize=16, fontweight='bold')
    ax2.axis("off")
    
    plt.tight_layout()
    map_path = MAP_DIR / "ghana_district_growth_2010_2021.png"
    plt.savefig(map_path, dpi=300, bbox_inches='tight')
    print(f"Saved district growth map to {map_path}")
    plt.close()

if __name__ == "__main__":
    create_regional_growth_map()
    create_district_growth_map()
