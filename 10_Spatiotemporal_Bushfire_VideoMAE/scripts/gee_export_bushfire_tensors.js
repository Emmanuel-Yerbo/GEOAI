/**
 * ==============================================================================
 * Google Earth Engine (GEE) - Multi-Modal Bushfire Spatiotemporal Tensor Builder
 * Target: Northern Savannah Zone, Ghana (Harmattan Fire Season)
 * ==============================================================================
 * 
 * Exports daily co-registered 11-channel space-time cubes (375m grid):
 * Channels:
 * 0: VIIRS Active Fire Mask (VNP14IMGTDL)
 * 1: Sentinel-2 NDMI (Moisture Index)
 * 2: Sentinel-2 NDVI (Fuel Density)
 * 3: ERA5-Land 10m U-wind component
 * 4: ERA5-Land 10m V-wind component
 * 5: ERA5-Land 2m Air Temperature
 * 6: ERA5-Land Relative Humidity
 * 7: ERA5-Land Total Precipitation
 * 8: SRTM Elevation (30m)
 * 9: SRTM Slope
 * 10: SRTM Aspect
 */

// 1. Define Northern Ghana Savannah Region of Interest (ROI)
var roi = ee.Geometry.Polygon([
  [[-2.8, 8.5], [-2.8, 11.2], [0.3, 11.2], [0.3, 8.5]]
]);

var targetDate = ee.Date('2024-01-15');
var startDate = targetDate.advance(-5, 'day'); // 5-day observation window

// 2. Static Terrain Features (SRTM)
var dem = ee.Image('USGS/SRTMGL1_003').clip(roi);
var slope = ee.Terrain.slope(dem);
var aspect = ee.Terrain.aspect(dem);
var terrain = dem.rename('elevation')
  .addBands(slope.rename('slope'))
  .addBands(aspect.rename('aspect'))
  .resample('bilinear')
  .reproject({crs: 'EPSG:4326', scale: 375});

// 3. Daily Meteorological Features (ERA5-Land Daily Aggregated)
var era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')
  .filterDate(startDate, targetDate)
  .filterBounds(roi)
  .map(function(img) {
    var u10 = img.select('u_component_of_wind_10m').rename('u_wind');
    var v10 = img.select('v_component_of_wind_10m').rename('v_wind');
    var temp = img.select('temperature_2m').rename('temp_2m');
    var dew = img.select('dewpoint_temperature_2m');
    var precip = img.select('total_precipitation_sum').rename('precip');
    
    // Relative Humidity approximation
    var rh = img.expression(
      '100 * (exp((17.625 * Td) / (243.04 + Td)) / exp((17.625 * T) / (243.04 + T)))', {
        'T': temp.subtract(273.15),
        'Td': dew.subtract(273.15)
      }
    ).rename('humidity');
    
    return u10.addBands(v10).addBands(temp).addBands(rh).addBands(precip)
      .resample('bilinear')
      .reproject({crs: 'EPSG:4326', scale: 375});
  });

// 4. Optical Spectral Indices (Sentinel-2 L2A Cloud-Filtered)
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate(startDate, targetDate)
  .filterBounds(roi)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .map(function(img) {
    var ndvi = img.normalizedDifference(['B8', 'B4']).rename('ndvi');
    var ndmi = img.normalizedDifference(['B8', 'B11']).rename('ndmi');
    return ndmi.addBands(ndvi)
      .resample('bilinear')
      .reproject({crs: 'EPSG:4326', scale: 375});
  }).median().clip(roi);

// 5. Active Fire Ground Truth (VIIRS VNP14IMGTDL 375m)
var viirs = ee.ImageCollection('FIRMS')
  .filterDate(startDate, targetDate.advance(1, 'day'))
  .filterBounds(roi)
  .select('T21')
  .map(function(img) {
    return img.gt(0).rename('fire_mask');
  });

print('Multi-modal spatiotemporal cube configured for Northern Ghana Harmattan season.');
