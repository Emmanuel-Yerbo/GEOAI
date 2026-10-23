# ==============================================================================
# Hexagonal Binning (Hexbin) Map of Ghana's Nighttime Lights
# ==============================================================================
# This script aggregates the high-resolution VIIRS nighttime lights raster into 
# a regular hexagonal grid. This creates a clean, stylized infographic map showing
# regional luminosity patterns across Ghana.

# Fix Windows PROJ database conflict (e.g. from PostgreSQL/PostGIS)
Sys.setenv(PROJ_LIB = system.file("proj", package = "sf"))

# 1. Load required libraries
library(sf)
library(terra)
library(tidyverse)
library(geodata)

# Set working directory to project folder
if (dir.exists("c:/YERBO/Desktop/CODING/R BASICS")) {
  setwd("c:/YERBO/Desktop/CODING/R BASICS")
}

# Ensure folders exist
dir.create("output", showWarnings = FALSE)

# ------------------------------------------------------------------------------
# 2. Load Administrative Boundary and Raster
# ------------------------------------------------------------------------------
message("1. Loading boundaries and VIIRS raster...")

# Get Ghana boundary at Level 0 (country outline)
ghana_vector <- gadm(country = "GHA", level = 0, path = "data", version = "latest") %>%
  st_as_sf()

# Load GEE-downloaded TIFF
viirs_raster_path <- "data/ghana_viirs_2023.tif"
if (!file.exists(viirs_raster_path)) {
  stop(paste("File not found at:", viirs_raster_path, "\nPlease run visualize_ghana_nightlights.R first to generate the local TIFF."))
}

viirs_raw <- rast(viirs_raster_path)
viirs_clamped <- clamp(viirs_raw, lower = 0)
viirs_log <- log1p(viirs_clamped)

# ------------------------------------------------------------------------------
# 3. Create Hexagonal Grid
# ------------------------------------------------------------------------------
message("2. Generating hexagonal grid...")

# We project to UTM Zone 30N (EPSG:32630) for Ghana so we can specify hexagon sizes in meters
ghana_utm <- st_transform(ghana_vector, 32630)

# Define hexagon size (width in meters)
# Lower values = smaller hexagons (more detail, slower to run)
# Higher values = larger hexagons (more generalized, faster)
HEX_SIZE_METERS <- 15000 # 15 km width

# Generate hexagonal grid
hex_grid_utm <- st_make_grid(
  ghana_utm,
  cellsize = HEX_SIZE_METERS,
  square = FALSE # FALSE creates hexagons
) %>%
  st_sf()

# Filter hexagons to only keep those intersecting Ghana's boundary
hex_grid_utm <- hex_grid_utm[st_intersects(hex_grid_utm, ghana_utm, sparse = FALSE), ]

# Crop the border hexagons to the exact coastline/borders of Ghana for a clean edge
hex_grid_cropped <- st_intersection(hex_grid_utm, ghana_utm)

# ------------------------------------------------------------------------------
# 4. Extract Nightlight Luminosity for each Hexagon
# ------------------------------------------------------------------------------
message("3. Extracting nightlight values for hexagons...")

# Project the cropped hexagons back to the raster's CRS (WGS84) for fast extraction
hex_grid_wgs84 <- st_transform(hex_grid_cropped, crs(viirs_log))

# Extract the median and maximum light intensity values in each hexagon
extracted_vals <- terra::extract(
  viirs_log, 
  vect(hex_grid_wgs84), 
  fun = mean, 
  na.rm = TRUE
)

# Append values back to the UTM grid for plotting
# The column name from the raster is 'avg_rad' (or the first band name)
band_name <- names(viirs_log)[1]
hex_grid_cropped$luminosity <- extracted_vals[[band_name]]

# Replace NA values (e.g. hexagons in water or outside data) with 0
hex_grid_cropped$luminosity[is.na(hex_grid_cropped$luminosity)] <- 0

# ------------------------------------------------------------------------------
# 5. Styling and Plotting
# ------------------------------------------------------------------------------
message("4. Styling and rendering plot...")

# Color Palette: Deep blue/purple -> Orange -> Gold -> White
hex_colors <- c("#110a26", "#5b2c6f", "#d35400", "#f1c40f", "#ffffff")

p_hex <- ggplot() +
  # Draw the binned hexagons
  geom_sf(
    data = hex_grid_cropped, 
    aes(fill = luminosity), 
    color = "#06060c", # Border color of each hexagon matching the background
    linewidth = 0.25
  ) +
  # Draw a subtle country boundary outline on top
  geom_sf(
    data = ghana_utm, 
    fill = "transparent", 
    color = "white", 
    linewidth = 0.4, 
    alpha = 0.3
  ) +
  # Custom scale fill matching our premium nightlights color ramp
  scale_fill_gradientn(
    colors = hex_colors,
    name = "Luminosity Index (Log Scale)",
    guide = guide_colorbar(
      title.position = "top",
      title.hjust = 0.5,
      barwidth = 15,
      barheight = 0.5,
      frame.colour = "transparent",
      ticks.colour = "#06060c"
    )
  ) +
  # Themes
  theme_void() +
  theme(
    panel.background = element_rect(fill = "#06060c", color = NA),
    plot.background = element_rect(fill = "#06060c", color = NA),
    legend.position = "bottom",
    legend.title = element_text(color = "gray80", size = 9, face = "bold"),
    legend.text = element_text(color = "gray60", size = 8),
    legend.margin = margin(t = 10, b = 15),
    plot.title = element_text(
      color = "white", 
      size = 18, 
      face = "bold", 
      hjust = 0.5, 
      margin = margin(t = 25, b = 5)
    ),
    plot.subtitle = element_text(
      color = "gray75", 
      size = 10, 
      hjust = 0.5, 
      margin = margin(b = 20)
    ),
    plot.caption = element_text(
      color = "gray45", 
      size = 7, 
      hjust = 0.5, 
      margin = margin(t = 15, b = 20)
    )
  ) +
  # Labels
  labs(
    title = "GHANA IN HEXAGONS",
    subtitle = "Aggregated nighttime lights (15km hexbins) showing key development clusters",
    caption = "Data: NASA Black Marble DNB (2023) | Cartography: R + sf + ggplot2 (15km equal-area grid)"
  )

# ------------------------------------------------------------------------------
# 6. Save and Display
# ------------------------------------------------------------------------------
output_file <- "output/ghana_nightlights_hexbin.png"
message(paste("5. Saving hexbin map to", output_file))

ggsave(
  filename = output_file,
  plot = p_hex,
  width = 8.5,
  height = 11,
  dpi = 400,
  bg = "#06060c"
)

# Export the spatial hexagonal polygons for use in other GIS software (QGIS, ArcGIS, etc.)
# We save in GeoPackage (industry standard) and GeoJSON format
message("Saving spatial vector files (GeoPackage & GeoJSON) for GIS software...")
st_write(
  hex_grid_cropped, 
  "output/ghana_nightlights_hexbins.gpkg", 
  delete_dsn = TRUE,
  quiet = TRUE
)
st_write(
  hex_grid_cropped, 
  "output/ghana_nightlights_hexbins.geojson", 
  delete_dsn = TRUE,
  quiet = TRUE
)

# Display static plot in RStudio Plots pane
print(p_hex)

# ------------------------------------------------------------------------------
# 7. Interactive Leaflet Hexbin Map Overlay (Viewer Pane)
# ------------------------------------------------------------------------------
message("\n6. Building interactive Leaflet hexbin map...")
library(leaflet)

# Reproject the cropped hexagons to WGS84 (EPSG:4326) for Leaflet compatibility
hex_grid_wgs84_display <- st_transform(hex_grid_cropped, 4326)

# Create color palette matching the gold/purple theme
pal_hex <- colorNumeric(
  palette = c("#140e2d", "#5b2c6f", "#d35400", "#f1c40f", "#ffffff"),
  domain = hex_grid_wgs84_display$luminosity,
  na.color = "transparent"
)

# Prepare HTML tooltips for interactive hover
tooltips <- sprintf(
  "<strong>15km Hexagonal Region</strong><br/><strong>Luminosity Index:</strong> %s",
  round(hex_grid_wgs84_display$luminosity, 3)
) %>% lapply(htmltools::HTML)

# Build interactive map
interactive_hex_map <- leaflet() %>%
  # Base Map Options
  addProviderTiles(providers$CartoDB.DarkMatter, group = "Dark Matter (OSM)") %>%
  addTiles(group = "OpenStreetMap (Standard)") %>%
  addProviderTiles(providers$Esri.WorldImagery, group = "Satellite Imagery") %>%
  
  # Hexagonal Vector Polygons
  addPolygons(
    data = hex_grid_wgs84_display,
    fillColor = ~pal_hex(luminosity),
    fillOpacity = 0.75,
    color = "#06060c", # Thin hex borders matching the theme
    weight = 0.8,
    opacity = 1,
    highlightOptions = highlightOptions(
      weight = 2,
      color = "#ffffff",
      bringToFront = TRUE
    ),
    label = tooltips,
    group = "Hexbins (15km)"
  ) %>%
  
  # Legend
  addLegend(
    pal = pal_hex,
    values = hex_grid_wgs84_display$luminosity,
    title = "Luminosity (Log)",
    position = "bottomright",
    group = "Hexbins (15km)"
  ) %>%
  
  # Layer Toggle Menu
  addLayersControl(
    baseGroups = c("Dark Matter (OSM)", "OpenStreetMap (Standard)", "Satellite Imagery"),
    overlayGroups = c("Hexbins (15km)"),
    options = layersControlOptions(collapsed = FALSE)
  )

# Display the interactive map in the RStudio Viewer pane
print(interactive_hex_map)

message("\nSuccess! Both the static hexbin map (Plots pane) and interactive hexbin map (Viewer pane) are ready.")
