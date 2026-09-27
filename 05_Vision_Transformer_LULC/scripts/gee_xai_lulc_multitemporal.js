// ============================================================================
// XAI for Multi-Temporal LULC Classification — GAMA, Ghana
// ============================================================================
// Sentinel-2 SR (2020, 2022, 2024) | 4 Classes | 25 Features per year
// Separate training polygons per year | Export CSV + TFRecord per year
// ============================================================================
//
// INSTRUCTIONS:
// 1. Digitize 4 polygon FeatureCollections PER YEAR in the GEE Geometry Tools.
//    Use Google Earth Pro historical imagery to verify land cover for each year.
//
//    Year 2020: BuiltUp_2020, Vegetation_2020, Water_2020, Bare_2020
//    Year 2022: BuiltUp_2022, Vegetation_2022, Water_2022, Bare_2022
//    Year 2024: BuiltUp_2024, Vegetation_2024, Water_2024, Bare_2024
//
//    Each polygon must have a property named 'class' with values:
//    1 = Built-Up, 2 = Vegetation, 3 = Water, 4 = Bare Soil
//
// 2. Make sure 'roi' is defined as your GAMA study area boundary.
// 3. Run the script — it will process all 3 years and queue 6 export tasks.
// ============================================================================


// ==============================
// SECTION 1: CONFIGURATION
// ==============================

// Define the three analysis years
var YEARS = [2020, 2022, 2024];

// Number of training samples per class per year
var SAMPLES_PER_CLASS = 800;

// LULC class definitions
var LABEL = 'class';
var CLASS_PALETTE = ['#E8453C', '#1B7A2F', '#2196F3', '#9E9E9E'];
// 1: Built-Up (red), 2: Vegetation (green), 3: Water (blue), 4: Bare Soil (grey)

// Map your manually digitized polygons PER YEAR here.
// Replace these with your actual FeatureCollection variable names.
var TRAINING_POLYGONS = {
  2020: BuiltUp_2020.merge(Vegetation_2020).merge(Water_2020).merge(Bare_2020),
  2022: BuiltUp_2022.merge(Vegetation_2022).merge(Water_2022).merge(Bare_2022),
  2024: BuiltUp_2024.merge(Vegetation_2024).merge(Water_2024).merge(Bare_2024)
};


// ==============================
// SECTION 2: CLOUD MASKING FUNCTION
// ==============================

function maskS2clouds(image) {
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}


// ==============================
// SECTION 3: COMPOSITE BUILDER (per year)
// ==============================
// Creates a cloud-free Sentinel-2 composite for a given year using
// the 15th percentile reducer (darkest clean pixels).

function buildComposite(year) {
  var startDate = year + '-01-01';
  var endDate = year + '-12-31';

  var composite_raw = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(maskS2clouds)
    .map(function(image) { return image.clip(roi); })
    .reduce(ee.Reducer.percentile([15]));

  // Rename bands: remove '_p15' suffix
  var allBandNames = composite_raw.bandNames();
  var newNames = allBandNames.map(function(name) {
    return ee.String(name).replace('_p15', '');
  });

  return composite_raw.rename(newNames);
}


// ==============================
// SECTION 4: FEATURE ENGINEERING (per composite)
// ==============================
// Builds a 25-band feature stack from a Sentinel-2 composite:
//   10 spectral bands + 7 indices + 5 GLCM textures + 3 terrain features

function buildFeatureStack(composite) {

  // --- 4A. Spectral Bands (10 features) ---
  var spectralBands = composite.select([
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'
  ]);

  // --- 4B. Vegetation & Land Indices (7 features) ---
  var ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI');

  var evi = composite.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
      'NIR': composite.select('B8'),
      'RED': composite.select('B4'),
      'BLUE': composite.select('B2')
  }).rename('EVI');

  var ndwi = composite.normalizedDifference(['B3', 'B8']).rename('NDWI');
  var ndbi = composite.normalizedDifference(['B11', 'B8']).rename('NDBI');

  var savi = composite.expression(
    '1.5 * ((NIR - RED) / (NIR + RED + 0.5))', {
      'NIR': composite.select('B8'),
      'RED': composite.select('B4')
  }).rename('SAVI');

  var bsi = composite.expression(
    '((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))', {
      'SWIR1': composite.select('B11'),
      'RED': composite.select('B4'),
      'NIR': composite.select('B8'),
      'BLUE': composite.select('B2')
  }).rename('BSI');

  var mndwi = composite.normalizedDifference(['B3', 'B11']).rename('MNDWI');

  // --- 4C. GLCM Texture Features (5 features) ---
  var nirInt = composite.select('B8').multiply(10000).toInt();
  var glcm = nirInt.glcmTexture({size: 3});

  var textureFeatures = glcm.select([
    'B8_contrast', 'B8_corr', 'B8_ent', 'B8_idm', 'B8_asm'
  ]).rename([
    'GLCM_Contrast', 'GLCM_Correlation', 'GLCM_Entropy',
    'GLCM_Homogeneity', 'GLCM_ASM'
  ]);

  // --- 4D. Topographic Features (3 features — static, same for all years) ---
  var dataset = ee.Image('USGS/SRTMGL1_003').clip(roi);
  var elevation = dataset.select('elevation').rename('Elevation');
  var slope = ee.Terrain.slope(dataset).rename('Slope');
  var aspect = ee.Terrain.aspect(dataset).rename('Aspect');

  // --- 4E. Stack All 25 Features ---
  var stack = spectralBands
    .addBands(ndvi).toFloat()
    .addBands(evi).toFloat()
    .addBands(ndwi).toFloat()
    .addBands(ndbi).toFloat()
    .addBands(savi).toFloat()
    .addBands(bsi).toFloat()
    .addBands(mndwi).toFloat()
    .addBands(textureFeatures).toFloat()
    .addBands(elevation).toFloat()
    .addBands(slope).toFloat()
    .addBands(aspect).toFloat();

  return stack;
}


// ==============================
// SECTION 5: TRAINING DATA EXTRACTION (per year)
// ==============================
// Converts digitized polygons into a class raster, then performs
// stratified random sampling within the polygons to extract
// training points with all 25 feature values.

function extractTraining(featureStack, polygons, year) {

  // Convert polygons to a temporary class image
  var polygonImage = polygons.reduceToImage({
    properties: [LABEL],
    reducer: ee.Reducer.first()
  }).rename(LABEL);

  // Perform stratified sampling within the digitized polygons
  var samples = featureStack.addBands(polygonImage).stratifiedSample({
    numPoints: SAMPLES_PER_CLASS,
    classBand: LABEL,
    region: roi,
    scale: 10,
    tileScale: 8,
    geometries: true
  });

  // Keep only features + class label
  var exportProperties = featureStack.bandNames().add(LABEL);
  samples = samples.select(exportProperties);

  return samples;
}


// ==============================
// SECTION 6: GEE RF QUICK-CHECK (per year)
// ==============================
// Trains a Random Forest classifier in GEE for a quick accuracy check
// and map visualization. The proper multi-algorithm comparison
// (RF, SVM, XGBoost) happens in the Python/Colab pipeline.

function quickClassify(featureStack, trainingSamples, year) {

  var bandNames = featureStack.bandNames();
  var rfClassifier = ee.Classifier.smileRandomForest(100)
    .train(trainingSamples, LABEL, bandNames);

  var classified = featureStack.classify(rfClassifier);

  // Add classified layer to map
  Map.addLayer(classified, {
    min: 1, max: 4,
    palette: CLASS_PALETTE
  }, 'RF LULC ' + year);

  // Print accuracy stats
  print(year + ' RF Training Accuracy:', rfClassifier.confusionMatrix().accuracy());
  print(year + ' RF Training Kappa:', rfClassifier.confusionMatrix().kappa());

  return classified;
}


// ==============================
// SECTION 7: EXPORT FUNCTIONS
// ==============================

// Export training CSV to Google Drive
function exportTrainingCSV(samples, year) {
  Export.table.toDrive({
    collection: samples,
    description: 'XAI_LULC_Training_' + year,
    folder: 'XAI_LULC_Ghana',
    fileNamePrefix: 'XAI_TRAINING_DATASET_' + year,
    fileFormat: 'CSV'
  });
}

// Export full 25-band feature stack as TFRecord for spatial prediction in Colab
function exportFeatureStackTFRecord(featureStack, year) {
  Export.image.toDrive({
    image: featureStack.toFloat(),
    description: 'XAI_LULC_GAMA_FeatureStack_' + year + '_TFRecord',
    folder: 'XAI_LULC_Ghana',
    fileNamePrefix: 'XAI_LULC_GAMA_FeatureStack_' + year + '_TFRecord',
    region: roi,
    scale: 10,
    fileFormat: 'TFRecord',
    formatOptions: {
      patchDimensions: [128, 128],
      compressed: true
    }
  });
}

// Export classified single-band GeoTIFF (RF quick-check)
function exportClassifiedMap(classified, year) {
  Export.image.toDrive({
    image: classified.uint8(),
    description: 'GAMA_LULC_RF_Map_' + year,
    folder: 'XAI_LULC_Ghana',
    fileNamePrefix: 'gama_lulc_rf_classified_' + year,
    region: roi,
    scale: 10,
    maxPixels: 1e9,
    fileFormat: 'GeoTIFF',
    fileDimensions: 10240
  });
}


// ==============================
// SECTION 8: MAIN PIPELINE — PROCESS ALL YEARS
// ==============================

Map.centerObject(roi, 10);

YEARS.forEach(function(year) {
  print('');
  print('=== Processing Year: ' + year + ' ===');

  // Step 1: Build cloud-free Sentinel-2 composite
  var composite = buildComposite(year);
  Map.addLayer(composite, {
    bands: ['B4', 'B3', 'B2'],
    min: 0.03, max: 0.28
  }, 'RGB ' + year, (year === 2024));  // Only show 2024 by default

  // Step 2: Build 25-band feature stack
  var featureStack = buildFeatureStack(composite);
  print(year + ' Feature Stack Bands:', featureStack.bandNames());
  print(year + ' Total Features:', featureStack.bandNames().size());

  // Step 3: Extract training samples from year-specific polygons
  var polygons = TRAINING_POLYGONS[year];
  var trainingSamples = extractTraining(featureStack, polygons, year);
  print(year + ' Total Training Samples:', trainingSamples.size());
  print(year + ' Class Balance:', trainingSamples.aggregate_histogram(LABEL));

  // Step 4: GEE RF quick-check classification
  var classified = quickClassify(featureStack, trainingSamples, year);

  // Step 5: Export training CSV + TFRecord feature stack
  exportTrainingCSV(trainingSamples, year);
  exportFeatureStackTFRecord(featureStack, year);
  exportClassifiedMap(classified, year);

  print('=== Year ' + year + ' exports queued ===');
});

print('');
print('============================================');
print('All 3 years processed. Check Tasks tab to');
print('start the 9 export tasks (3 per year):');
print('  - Training CSV');
print('  - Feature Stack TFRecord');
print('  - RF Classified Map GeoTIFF');
print('============================================');
