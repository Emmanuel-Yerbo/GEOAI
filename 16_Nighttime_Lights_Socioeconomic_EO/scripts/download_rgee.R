# ==============================================================================
# Programmatic Download of Ghana Nightlights using Google Earth Engine (rgee)
# ==============================================================================
# This script initializes Earth Engine in R, queries the 2023 VIIRS Nighttime Lights 
# composite, clips it to Ghana, and exports it locally to 'data/ghana_viirs_2023.tif'.

# 1. Install/Load required packages
required_packages <- c("rgee", "sf", "terra", "googledrive")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if (length(new_packages)) {
  message("Installing missing packages: ", paste(new_packages, collapse = ", "))
  install.packages(new_packages)
}

library(sf)
library(terra)
library(rgee)
library(googledrive)

# Create data directory if it doesn't exist
dir.create("data", showWarnings = FALSE)

# 2. Initialize Earth Engine
# (If running for the first time, this will prompt you to authenticate your 
# Google Earth Engine account and Google Drive account in your browser)
message("\nInitializing Google Earth Engine...")
ee_Initialize(drive = TRUE)

# 3. Load Ghana Boundary from GEE's LSIB dataset
message("Fetching Ghana boundary from GEE LSIB...")
ghana_ee <- ee$FeatureCollection("USDOS/LSIB_SIMPLE/2017") %>%
  ee$FeatureCollection$filter(ee$Filter$eq("country_na", "Ghana"))

# 4. Load NOAA VIIRS Monthly Nighttime Lights (2023 median)
message("Loading NOAA VIIRS Monthly Nighttime Lights (2023)...")
viirs_ee <- ee$ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG") %>%
  ee$ImageCollection$filterDate("2023-01-01", "2023-12-31") %>%
  ee$ImageCollection$select("avg_rad") %>%
  ee$ImageCollection$median() %>%
  ee$Image$clip(ghana_ee)

# 5. Export from Earth Engine to local directory via Google Drive
# We use via = "drive" since Ghana's area is too large for the instant "getInfo" limit.
output_path <- "data/ghana_viirs_2023.tif"

message("Downloading raster to '", output_path, "' (this will take 1-2 minutes)...")
viirs_local <- ee_as_rast(
  image = viirs_ee,
  region = ghana_ee$geometry(),
  scale = 463, # VIIRS native resolution (~15 arc-seconds)
  via = "drive",
  dsn = output_path
)

if (file.exists(output_path)) {
  message("\nSuccess! Crop saved to: ", output_path)
  message("Now open 'visualize_ghana_nightlights.R' and run it with DOWNLOAD_PROGRAMMATICALLY <- FALSE.")
} else {
  stop("Download failed or file was not saved.")
}
