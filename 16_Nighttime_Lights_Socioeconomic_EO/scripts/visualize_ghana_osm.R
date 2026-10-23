# ==============================================================================
# Interactive Overlay of Ghana Nighttime Lights on OpenStreetMap (OSM)
# ==============================================================================
# This script loads your processed VIIRS raster and displays it as an interactive 
# leaflet map, letting you pan/zoom and toggle between standard OSM, Dark Matter, 
# and Satellite basemaps with custom transparency controls.

# 1. Install & Load packages
required_packages <- c("leaflet", "terra", "sf", "raster")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if (length(new_packages)) {
  message("Installing missing packages: ", paste(new_packages, collapse = ", "))
  install.packages(new_packages)
}

library(sf)
library(terra)
library(raster)
library(leaflet)

# Set working directory to project directory
if (dir.exists("c:/YERBO/Desktop/CODING/R BASICS")) {
  setwd("c:/YERBO/Desktop/CODING/R BASICS")
}

# 2. Load and process the local raster
viirs_raster_path <- "data/ghana_viirs_2023.tif"
if (!file.exists(viirs_raster_path)) {
  stop(paste("Raster file not found at:", viirs_raster_path, "\nPlease run visualize_ghana_nightlights.R first."))
}

message("Loading local raster...")
viirs_raw <- rast(viirs_raster_path)
viirs_clamped <- clamp(viirs_raw, lower = 0)
viirs_log <- log1p(viirs_clamped)

# 3. Reproject to WGS84 (EPSG:4326) for Leaflet compatibility
message("Reprojecting raster for interactive viewer...")
viirs_wgs84 <- project(viirs_log, "EPSG:4326")

# Convert to standard Raster class for universal Leaflet compatibility
viirs_legacy <- raster::raster(viirs_wgs84)

# 4. Create a custom color palette (transparent background, violet-to-gold-to-white)
pal <- colorNumeric(
  palette = c("#140e2d", "#5b2c6f", "#d35400", "#f1c40f", "#ffffff"),
  domain = values(viirs_legacy),
  na.color = "transparent"
)

# 5. Build and render the Interactive Leaflet Map
message("\nBuilding interactive map...")
map <- leaflet() %>%
  # Option A: CartoDB Dark Matter (Recommended: highlights nightlights beautifully)
  addProviderTiles(providers$CartoDB.DarkMatter, group = "Dark Matter (OSM)") %>%
  
  # Option B: Standard OpenStreetMap
  addTiles(group = "OpenStreetMap (Standard)") %>%
  
  # Option C: Esri World Imagery (Satellite background)
  addProviderTiles(providers$Esri.WorldImagery, group = "Satellite Imagery") %>%
  
  # Add the VIIRS Nightlights Layer
  addRasterImage(
    viirs_legacy,
    colors = pal,
    opacity = 0.7,
    group = "VIIRS Nightlights 2023",
    project = FALSE
  ) %>%
  
  # Add Legend
  addLegend(
    pal = pal,
    values = values(viirs_legacy),
    title = "Luminosity (Log Scale)",
    position = "bottomright",
    group = "VIIRS Nightlights 2023"
  ) %>%
  
  # Layer controls (base layers and overlay layers)
  addLayersControl(
    baseGroups = c("Dark Matter (OSM)", "OpenStreetMap (Standard)", "Satellite Imagery"),
    overlayGroups = c("VIIRS Nightlights 2023"),
    options = layersControlOptions(collapsed = FALSE)
  )

# Display the map in RStudio Viewer / Web Browser
print(map)

message("\nSuccess! The interactive map is rendering in your Viewer pane.")
