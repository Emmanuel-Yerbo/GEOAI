# Spatial Autocorrelation & Land Surface Temperature Hotspot Modeling
## Case Study: 24-Year Urban Heat Island Trajectories & District Microclimates in Ghana

[![PySAL](https://img.shields.io/badge/PySAL-ESDA%20%7C%20libpysal-orange)](https://pysal.org/)
[![Rasterio](https://img.shields.io/badge/Rasterio-Geospatial%20Rasters-blue)](https://rasterio.readthedocs.io/)
[![Landsat](https://img.shields.io/badge/Sensor-Landsat%20TIR%20C2-green)](https://usgs.gov)

### 1. Introduction: The Spatial Logic of Urban Thermal Autocorrelation
Urban microclimates are non-random geographic phenomena governed by **spatial autocorrelation** (Tobler's First Law of Geography). High Land Surface Temperature (LST) values cluster together in areas with dense impervious surfaces, depleted canopy cover, and industrial activity.

This project implements an automated spatial data science pipeline combining multi-temporal **Landsat Thermal Infrared (TIR)** split-window retrieval algorithms with **PySAL** spatial autocorrelation statistics to isolate statistically significant thermal corridors across Ghanaian districts from 2000 to 2024.

---

### 2. Methodological Pipeline

#### 2.1 Split-Window Radiometric LST Retrieval
- **The Process**: Landsat 7, 8, and 9 Collection 2 Level-2 thermal bands are converted into Top-of-Atmosphere (TOA) spectral radiance and absolute surface temperature in Celsius ($^\circ	ext{C}$).
- **The Essence**: Radiative transfer corrections account for atmospheric attenuation and fractional vegetation cover (FVC) derived from Sentinel/Landsat NDVI.

#### 2.2 Spatial Autocorrelation Statistics (Getis-Ord $G_i^*$ & LISA)
- **The Process**: Thermal raster centroids are projected and connected via distance-band spatial weight matrices ($W$). We calculate local Getis-Ord $G_i^*$ z-scores with 999 Monte Carlo permutations.
- **The Essence**: Separates true, statistically significant thermal hotspots ($p < 0.01$, $z > +2.58$) from random temperature fluctuations, providing rigorous mathematical proof of localized Urban Heat Islands (UHI).

---

### 3. Scenario Analysis: Spatial Insights

#### Scenario 1: Thermal Corridor Spotlight (Afram Plains LST Retrieval)
- **Purpose**: Delineating absolute baseline land surface temperature patterns across rural-urban interfaces.

<p align="center">
  <img src="results/afram_smooth_lst.png" width="600" alt="Smooth LST Map">
</p>

- **Insight**: Reveals severe thermal gradient divergence. Core agricultural clearings and bare soils register temperatures $6.2^\circ	ext{C}$ to $9.5^\circ	ext{C}$ higher than adjacent riparian wetlands and forested reserves.

#### Scenario 2: Multi-Temporal Getis-Ord $G_i^*$ Hotspot Clustering (2000–2024)
- **Purpose**: Mapping the 24-year geographic evolution of statistically confirmed thermal corridors across Sekyere, Atebubu, and Afram districts.

<p align="center">
  <img src="results/hotspot_maps_2000_2024.png" width="900" alt="Getis Ord Hotspots">
</p>

- **Insight**: Pinpoints persistent **thermal inertia corridors**. Hotspots with $99\%$ statistical confidence ($z > +2.58$) have expanded by $131.5\%$ since 2000, aligning tightly with corridors of rapid urban built-up expansion and highway corridors.

#### Scenario 3: Decadal District Thermal Trajectories
- **Purpose**: Longitudinal temporal trend analysis of mean LST dynamics across multiple administrative jurisdictions.

<p align="center">
  <img src="results/lst_temporal_trends.png" width="900" alt="LST Temporal Trends">
</p>

- **Insight**: Quantifies steady warming trajectories across all monitored districts, providing empirical climatological evidence of localized Anthropogenic Urban Heat Island intensification.

#### Scenario 4: Hexagonal Spatial Disaggregation & Infrastructure Adequacy (Uber H3 Res 8)
- **Purpose**: Moving beyond arbitrary administrative boundaries by indexing micro-urban infrastructure indicators into equal-area hexagonal tessellations (Uber H3 Resolution 8, ~460m aperture).

<p align="center">
  <img src="results/accra_h3_infrastructure_adequacy.png" width="850" alt="Greater Accra H3 Hexagonal Infrastructure Adequacy">
  <br>
  <em>Figure 4: Greater Accra H3 Res 8 Hexagonal Infrastructure Adequacy Score (2025).</em>
</p>

- **Insight**: Eliminates Modifiable Areal Unit Problem (MAUP) artifacts. Identifies high-adequacy service clusters (green/cyan) in core Accra and Tema, juxtaposed against severe infrastructure deficits (dark red/orange) along the rapidly expanding peripheral sprawl belt.

#### Scenario 5: Unsupervised Spatial Urban Typologies (K-Means Clustering, $k=7$)
- **Purpose**: Classify discrete urban spatial fabrics by jointly clustering road density, building footprint morphology, LST thermal stress, and service proximity.

<p align="center">
  <img src="results/unsupervised_urban_typology_kmeans.png" width="850" alt="Unsupervised Urban Typology Classification">
  <br>
  <em>Figure 5: Unsupervised Urban Typology Classification (K-Means, k=7) across Greater Accra.</em>
</p>

- **Insight**: Discovers 7 distinct morphological zones:
  - *Cluster 0 & 1*: Historic dense commercial and transportation corridors (blue/cyan).
  - *Cluster 2 & 3*: Established suburban fabric and transitional peri-urban zones (green/orange).
  - *Cluster 4 & 6*: Unserviced sprawl frontiers and high-density informal settlements (red/purple), which correlate with maximum thermal vulnerability.

#### Scenario 6: 3D Interactive WebGL Spatial Clustering & Global Moran's I
- **Purpose**: Render continuous 3D interactive height extrusions representing spatial clustering intensity, validated with global spatial statistics.

<p align="center">
  <img src="results/pydeck_3d_spatial_moran.png" width="850" alt="3D PyDeck WebGL Map and Moran Significance">
  <br>
  <em>Figure 6: 3D interactive PyDeck WebGL extrusion map with confirmed Global Moran's I (p < 0.001).</em>
</p>

- **Insight**: Confirms strong spatial clustering with statistical significance ($p < 0.001$). The 3D hexagonal pillars visually communicate the spatial concentration of infrastructure disparity and urban thermal burdens to non-technical policy stakeholders.

---

### 4. Planning & Public Health Implications
Identifying statistically validated thermal hotspots and infrastructure disparities enables municipal physical planning authorities to formulate targeted **Urban Heat & Infrastructure Mitigation Strategies**:
1. **Targeted Urban Greening:** Directing municipal tree-planting budgets to the exact $99\%$ confidence hotspots rather than deploying canopy uniformly.
2. **Cool Pavement Zoning:** Mandating high-albedo roofing and permeable pavement standards in diagnosed thermal corridors to lower ambient temperatures and reduce heat stress vulnerability among low-income outdoor workers.
3. **Hexagonal Infrastructure Allocation:** Utilizing H3 Res 8 spatial units to direct water, transit, and electrical grid capital investments directly into the red deficit zones.

