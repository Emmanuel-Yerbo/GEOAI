/**
 * Multi-Criteria Cloud Flood Susceptibility Modeling in Google Earth Engine
 * Author: Emmanuel Yerbo
 */

// 1. Study Area: Volta Region, Ghana
var aoi = ee.FeatureCollection("FAO/GAUL/2015/level1")
  .filter(ee.Filter.eq('ADM1_NAME', 'Volta'));

// 2. Data Sources
var srtm = ee.Image("USGS/SRTMGL1_003").clip(aoi);
var slope = ee.Terrain.slope(srtm);
var meritHand = ee.Image("MERIT/Hydro/v1_0_1").select('hnd').clip(aoi);
var jrcWater = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select('occurrence').clip(aoi);
var worldCover = ee.Image("ESA/WorldCover/v100/2020").select('Map').clip(aoi);

// 3. Multi-Criteria Weighted Overlay
// Normalization & Weighting: HAND (30%), Slope (25%), JRC Water (25%), Elevation (20%)
var handScore = meritHand.unitScale(0, 50).multiply(-1).add(1);
var slopeScore = slope.unitScale(0, 30).multiply(-1).add(1);
var jrcScore = jrcWater.divide(100);
var elevScore = srtm.unitScale(0, 500).multiply(-1).add(1);

var floodIndex = handScore.multiply(0.30)
  .add(slopeScore.multiply(0.25))
  .add(jrcScore.multiply(0.25))
  .add(elevScore.multiply(0.20));

// 4. Visualization & Zonation
var floodZones = floodIndex.gt(0.65).rename('high_susceptibility');
Map.centerObject(aoi, 8);
Map.addLayer(floodIndex, {min: 0, max: 1, palette: ['green', 'yellow', 'orange', 'red']}, 'Flood Susceptibility Index');
Map.addLayer(floodZones.selfMask(), {palette: ['blue']}, 'High Flood Susceptibility Zone');
