# 🌡️ Spatial Autocorrelation & Land Surface Temperature Hotspot Modeling

[![PySAL](https://img.shields.io/badge/PySAL-ESDA%20%7C%20libpysal-orange)](https://pysal.org/)
[![Rasterio](https://img.shields.io/badge/Rasterio-Geospatial%20Rasters-blue)](https://rasterio.readthedocs.io/)
[![Landsat](https://img.shields.io/badge/Sensor-Landsat%20TIR%20C2-green)](https://usgs.gov)

## 📌 Overview
An automated Python spatial data science pipeline combining multi-temporal **Landsat Thermal Infrared (TIR)** split-window Land Surface Temperature (LST) retrieval with spatial autocorrelation modeling in **PySAL**.

### Methodological Framework:
1. **Split-Window LST Retrieval:** Converts Landsat 7/8/9 Collection 2 Level-2 Thermal Infrared bands into absolute surface temperature ($^\circ	ext{C}$) corrected for atmospheric transmission and fractional vegetation cover (FVC).
2. **Spatial Autocorrelation Statistics:**
   - **Getis-Ord $G_i^*$ Statistics:** Computed with 999 Monte Carlo permutations across projected distance-band spatial weight matrices ($W$) to isolate statistically significant extreme heat corridors ($p < 0.01$, $z > +2.58$).
   - **Anselin Local Moran's I (LISA):** Pinpoints High-High thermal clusters and spatial outliers.
3. **Multi-Temporal Dynamics:** Tracks 20-year urban heat island trajectory across the Accra Metropolis and regional districts, correlating extreme thermal hotspots with 131.5% built-up expansion.
