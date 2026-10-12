// Complete 9 GeoAI Projects structured in the 4-Tier Project Narrative
const PROJECTS_DATA = [
  {
    id: "01_VegHealthCNN",
    num: "01",
    title: "VegHealthCNN: Spectral-Temporal 1D-CNN for Precision Agriculture",
    category: "agri",
    catLabel: "Precision Agriculture",
    tech: ["PyTorch", "Sentinel-2 L2A", "Spatial Block CV", "GroupKFold"],
    summary: "57k-parameter 1D-CNN achieving 98.7% test accuracy across 301 spatially isolated field samples, projecting a 19.5% reduction in synthetic nitrogen demand.",
    tier1_problem: "Smallholder crop mosaics in sub-Saharan Africa suffer from extreme spatial heterogeneity and nutrient volatility, leading to inefficient blanket fertilizer application and high agricultural runoff.",
    tier2_pipeline: "We engineered a custom 57,091-parameter 1D-Convolutional Neural Network in PyTorch trained on multi-temporal Sentinel-2 spectral-temporal signatures, strictly evaluated using spatial block cross-validation (GroupKFold across 0.01° spatial blocks) to eliminate spatial autocorrelation data leakage.",
    tier3_validation: "Achieved 98.7% test accuracy across 301 spatially independent samples (vs 99.4% in naive random split with severe spatial autocorrelation leakage). Confusion matrix proves 97.5% producer accuracy on stressed crops.",
    tier4_impact: "Formulated variable-rate nitrogen prescriptions that project a 19.5% reduction in synthetic fertilizer demand (~4.02 million kg N), safeguarding peri-urban agrarian catchments from runoff.",
    diagram: `Cross-Validation Strategy   | Test Accuracy | Cohen's Kappa | Spatial Autocorrelation Bias
----------------------------+---------------+---------------+------------------------------
Naive Random K-Fold Split   | 99.4%         | 0.991         | HIGH (Severe Data Leakage)
Spatial Block CV (0.01° Grid)| 98.7%         | 0.982         | ZERO LEAKAGE (Independent)

CONFUSION MATRIX (301 Spatially Isolated Samples):
                 Predicted Stressed  Predicted Moderate  Predicted Healthy
Actual Stressed:        78                   2                   0
Actual Moderate:         1                  118                  1
Actual Healthy:          0                   0                  101`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/01_VegHealthCNN"
  },
  {
    id: "02_FrostWatch_Arctic",
    num: "02",
    title: "FrostWatch Arctic: Retrogressive Thaw Slump Semantic Segmentation",
    category: "disaster",
    catLabel: "Climate & Cryosphere",
    tech: ["UNet++", "DeepLabV3+", "MAnet", "13-Ch Tensor", "Area Loss"],
    summary: "Three-arm semantic ensemble with 13-channel geomorphometric input tensors, placing Top 5 Globally (16.45 AP) in the 2026 Cyber2A Arctic Challenge.",
    tier1_problem: "Accelerating Arctic warming triggers catastrophic retrogressive thaw slumps, threatening critical circumpolar infrastructure with non-linear terrain collapse.",
    tier2_pipeline: "Engineered a three-arm mean-fusion semantic ensemble combining UNet++ (SE-ResNeXt50), DeepLabV3+ (EfficientNet-B5), and MAnet (MiT-B5) fed with 13-channel geomorphometric tensors (optical bands + Sobel slope + Laplacian curvature + elevation) and size-weighted area-attenuated loss.",
    tier3_validation: "Placed 5th internationally (16.45 AP) among 15 international research institutions in the 2026 GeoAI Arctic Challenge (Cyber2A), improving boundary recall on small thaw slumps (<500 m²) by +24.3%.",
    tier4_impact: "Delivers an operational geomorphological risk mapping model for northern circumpolar civil engineering, identifying active slope failure zones prior to catastrophic collapse.",
    diagram: `Ensemble Model Architecture        | Encoders                  | Channels | COCO AP Score
-----------------------------------+---------------------------+----------+--------------
UNet++ + DeepLabV3+ + MAnet        | SE-ResNeXt50/EffNet/MiT   | 13 Bands | 16.45 (TOP 5)
Single Model UNet++                | SE-ResNeXt50              | 13 Bands | 14.12 AP
Baseline DeepLabV3+                | ResNet-50                 | 3 Bands  | 11.20 AP`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/02_FrostWatch_Arctic"
  },
  {
    id: "03_Building_Extraction",
    num: "03",
    title: "Nationwide Building Footprint Extraction with SegFormer",
    category: "vision",
    catLabel: "Foundation Models",
    tech: ["SegFormer-B3", "TorchGeo", "30cm VHR Aerial", "ONNX Runtime"],
    summary: "Fine-tuned SegFormer-B3 extracting dense informal building footprints across Ghana, achieving 57.9% IoU where global catalogs merge contiguous roofs.",
    tier1_problem: "Dense informal urbanization across West African metropolitan cores features contiguous corrugated zinc roofs separated by <1.5m alleys, causing global AI building catalogs to merge dwellings into massive irregular polygons.",
    tier2_pipeline: "Fine-tuned SegFormer-B3 and U-Net architectures using TorchGeo spatial samplers over 30cm very high-resolution aerial imagery, benchmarking against Google Open Buildings, Overture Maps, and OpenStreetMap.",
    tier3_validation: "Achieved 57.9% Intersection over Union (IoU) with 84.6% precision, resolving alley separations in dense Accra and Kumasi informal settlements. Exported quantized ONNX runtime weights for municipal edge inference.",
    tier4_impact: "Provides municipal physical planning departments with actionable cadastre footprint layers for property rate valuation, emergency routing, and statutory local structure schemes.",
    diagram: `Data Source / Model                | Precision | Recall  | Intersection-over-Union (IoU)
-----------------------------------+-----------+---------+-------------------------------
SegFormer-B3 Fine-Tuned (Ours)     | 84.6%     | 79.2%   | 57.9% (ONNX Runtime)
Google Open Buildings (V3)         | 76.1%     | 68.4%   | 48.2% (Merged Polygons)
OpenStreetMap (OSM Crowdsourced)   | 91.2%     | 41.5%   | 39.8% (Severe omissions)`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/03_Building_Extraction"
  },
  {
    id: "04_XAI_Flood_GradCAM",
    num: "04",
    title: "Explainable AI (XAI) Flood Inundation Prediction with Grad-CAM",
    category: "disaster",
    catLabel: "Flood & Disaster Risk",
    tech: ["U-Net", "PyTorch", "Grad-CAM Hooks", "Drone UAV Imagery"],
    summary: "Coupled U-Net with Grad-CAM backpropagation hooks, attaining 87% accuracy and 72% IoU on Akosombo dam spillage aerial drone imagery with verifiable decision heatmaps.",
    tier1_problem: "Deploying black-box deep learning models in emergency disaster response carries life-or-death risk: standard CNNs can mistakenly classify asphalt cloud shadows as open floodwater.",
    tier2_pipeline: "Coupled an encoder-decoder U-Net with Gradient-Weighted Class Activation Mapping (Grad-CAM) to evaluate sub-meter UAV drone aerial imagery, backpropagating gradients directly from the classification head to final convolutional feature maps.",
    tier3_validation: "Attained 87% overall accuracy and 72% IoU. Grad-CAM visual decision heatmaps verified that neural activations were concentrated on specular water reflections and inundated residential parcels rather than sensor artifacts.",
    tier4_impact: "Delivered rapid inundation extent maps for emergency rescue operations in the Lower Volta Basin following the 2023 Akosombo Dam spillage.",
    diagram: `Target Feature              | Model Prediction | Grad-CAM Attention | Verification
----------------------------+------------------+--------------------+-------------------
Inundated Farmland / Crops  | Water (1.00)     | High gradient peak | Validated True Pos
Submerged Residential Roads | Water (0.96)     | High margin        | Validated True Pos
Dry Asphalt Cloud Shadow    | Non-Water (0.04) | Zero activation    | Robust (No Leak)
Overall Accuracy: 87.4% | Intersection over Union (IoU): 72.1% | F1-Score: 0.838`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/04_XAI_Flood_GradCAM"
  },
  {
    id: "05_Vision_Transformer_LULC",
    num: "05",
    title: "Vision Transformers & Tree SHAP for Land Cover Attribution",
    category: "vision",
    catLabel: "XAI & Transformers",
    tech: ["Swin Transformer", "SegFormer", "Tree SHAP", "Sentinel-2 SAR/Opt"],
    summary: "Shifted-window transformer attention achieving 91.3% LULC accuracy in heterogeneous transition savannah, with SHAP force plots explaining 42% predictive gain from Red-Edge bands.",
    tier1_problem: "Semi-arid and transitional agro-pastoral savannah ecotones suffer from severe spectral overlap between bare soil, degraded shrubs, and rainfed subsistence cropland.",
    tier2_pipeline: "Implemented an explainable GeoAI architecture integrating Vision Transformers (SegFormer and Swin Transformer) with Tree SHAP cooperative game theory over multi-temporal Sentinel-2 optical and SAR time-series.",
    tier3_validation: "Achieved 91.3% overall classification accuracy across heterogeneous landscapes. SHAP force plots proved that Sentinel-2 Red-Edge Band 5 and NDRE contributed 42% of marginal predictive gain for agricultural classes.",
    tier4_impact: "Presented orally at the Ghana Geographical Association (GGA) and GeoAI4SD 2026 conferences to guide agricultural subsidy and drought risk zoning.",
    diagram: `Class Name        | Cropland | Forest | Shrubland | Bare Soil | User Accuracy
------------------+----------+--------+-----------+-----------+--------------
Cropland (Rainfed)|   412    |   8    |    15     |    11     |    92.3%
Dense Forest      |    11    |  389   |    14     |     0     |    93.5%
Open Shrubland    |    22    |   19   |   341     |    18     |    85.3%
Bare / Degraded   |     9    |   0    |    12     |   298     |    93.4%
Overall Accuracy: 91.3% | Cohen's Kappa: 0.887`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/05_Vision_Transformer_LULC"
  },
  {
    id: "06_SAMGeo_Infrastructure",
    num: "06",
    title: "SAMGeo Foundation Models for Zero-Shot Spatial Infrastructure",
    category: "vision",
    catLabel: "Foundation Models",
    tech: ["Meta SAM", "SAMGeo", "LangSAM", "Grounding DINO", "ViT-Huge"],
    summary: "Zero-shot foundation model pipeline segmenting 1,420 structures with zero task-specific retraining, eliminating weeks of manual digitizing.",
    tier1_problem: "Traditional spatial infrastructure auditing requires weeks of manual digitizing or hundreds of thousands of labeled training polygons that municipal assemblies cannot afford to produce.",
    tier2_pipeline: "Operationalized Meta AI's Segment Anything Model (SAM) and LangSAM with Vision Transformer (ViT) backbones, applying text-prompted zero-shot semantic segmentation over sub-meter drone orthomosaics across campus and aviation facilities in Ghana.",
    tier3_validation: "Extracted 1,420 building boundaries and paved assets with sub-meter geometric delineation in minutes with zero task-specific retraining (74.8% building IoU, 82.1% runway IoU).",
    tier4_impact: "Demonstrates how open-source foundation models democratize spatial asset mapping for resource-constrained African municipal assemblies.",
    diagram: `Prompt / Class           | Backbone Architecture | Retraining Needed | Boundary IoU
-------------------------+-----------------------+-------------------+--------------
'building' (Footprint)   | ViT-Huge (SAM)        | NONE (Zero-Shot)  | 74.8%
'runway' / 'taxiway'     | Grounding DINO + SAM  | NONE (Zero-Shot)  | 82.1%
'tree canopy'            | ViT-Large (SAMGeo)    | NONE (Zero-Shot)  | 69.4%
'aircraft'               | LangSAM (Text Prompt) | NONE (Zero-Shot)  | 86.5%`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/06_SAMGeo_Infrastructure"
  },
  {
    id: "07_GEE_Flood_Susceptibility",
    num: "07",
    title: "Cloud-Based Multi-Criteria Flood Risk Modeling in Google Earth Engine",
    category: "disaster",
    catLabel: "Flood & Disaster Risk",
    tech: ["Google Earth Engine", "MERIT Hydro HAND", "SRTM 30m", "JRC GSW"],
    summary: "Cloud-native GEE pipeline identifying 37.5% of the Lower Volta Basin as high-to-severe flood risk zones, validated against historical NADMO disaster records.",
    tier1_problem: "Seasonal monsoon rainfall and hydro-dam spillages repeatedly displace riverine communities across the Volta Basin, while municipal planners lack real-time cloud-native tools to forecast regional vulnerability.",
    tier2_pipeline: "Developed an automated multi-criteria weighted overlay pipeline in the GEE JavaScript API, fusing SRTM 30m DEM elevation, slope gradients, MERIT Hydro HAND, JRC 24-year surface water recurrence, and ESA WorldCover 10m.",
    tier3_validation: "Delineated 37.5% of the lower basin as high-to-severe flood risk zones, matching historical ground disaster records from the National Disaster Management Organisation (NADMO).",
    tier4_impact: "Produced spatial zoning layers adopted to guide regional emergency evacuation corridors and flood-resilient land-use permits.",
    diagram: `Parameter (AHP Weights)             | Source & Resolution      | Criterion Weight
------------------------------------+--------------------------+------------------
Height Above Nearest Drainage (HAND)| MERIT Hydro (90m)        | 30% (Hydraulic)
Elevation & Slope Gradients         | SRTM 1 Arc-Second (30m)  | 25% (Ponding)
Historical Flood Recurrence (00-24) | JRC Global Surface Water | 20% (History)
Land Use / Impervious Cover         | ESA WorldCover (10m)     | 15% (Runoff)
Proximity to Major Drainage Channels| HydroSHEDS River Network | 10% (Overflow)`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/07_GEE_Flood_Susceptibility"
  },
  {
    id: "08_PySAL_LST_Hotspots",
    num: "08",
    title: "24-Year Urban Heat Island Autocorrelation & Microclimate Modeling",
    category: "urban",
    catLabel: "Urban Planning & Climate",
    tech: ["PySAL ESDA", "libpysal", "Landsat TIR C2", "Getis-Ord Gi*", "Moran's I"],
    summary: "Undergraduate Honors Thesis analyzing 24-year Landsat thermal trajectories, proving statistically significant (p < 0.001) outward migration of thermal hotspots into peri-urban Accra.",
    tier1_problem: "Rapid, unregulated urban expansion across Greater Accra has converted vital agricultural and vegetative cooling corridors into dense impervious surfaces, escalating local microclimatic thermal distress.",
    tier2_pipeline: "Ingested 24 years (2000–2024) of multi-temporal Landsat Thermal Infrared (TIR) Collection 2 calibrated radiometry, applying Rasterio and PySAL to compute global and local spatial autocorrelation metrics (Moran's I and Getis-Ord Gi* hot spot analytics).",
    tier3_validation: "Proved statistically significant (p < 0.001) spatial clustering of thermal extremes, tracking the progression of Moran's I from 0.482 in 2000 to 0.647 in 2024.",
    tier4_impact: "Established empirical evidence for Accra's climate resilience strategy and urban green-belt zoning policies to mitigate severe microclimatic heating.",
    diagram: `Year | Mean LST (°C) | Moran's I (Spatial Clustering) | p-value | Hotspots (Gi*)
-----+---------------+--------------------------------+---------+---------------------------
2000 | 28.4°C        | 0.482                          | < 0.001 | Industrial / Port Core
2010 | 31.1°C        | 0.541                          | < 0.001 | Central Accra Sprawl
2020 | 33.6°C        | 0.618                          | < 0.001 | Northern Peri-Urban Fringe
2024 | 34.2°C        | 0.647                          | < 0.001 | Corridors (Adenta, Ga East)

LISA QUADRANTS: Hotspots (HH): 28.4% | Cool Islands (LL): 18.2% | Outliers: 6.1%`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/08_PySAL_LST_Hotspots"
  },
  {
    id: "09_Network_Accessibility_15MinCity",
    num: "09",
    title: "15-Minute City Network Isochrones & Healthcare Transit Equity",
    category: "urban",
    catLabel: "Urban Planning & Mobility",
    tech: ["OSMnx", "NetworkX Dijkstra", "PyDeck 3D", "Uber H3", "Isochrones"],
    summary: "Topological pedestrian network graph modeling showing 41.8% of peri-urban residents live in healthcare deserts outside the 15-minute walking catchment in Greater Accra.",
    tier1_problem: "Polycentric urban sprawl in Greater Accra creates acute healthcare deserts, where rapid settlement expansion leaves residents without pedestrian walking access to emergency public clinics.",
    tier2_pipeline: "Constructed topological walkable graph networks from OpenStreetMap data using OSMnx, executing NetworkX Dijkstra shortest-path algorithms and convex hull geometric buffering to generate 5, 10, and 15-minute walking isochrones rendered in PyDeck 3D WebGL.",
    tier3_validation: "Revealed that while 93.8% of urban core residents reach primary clinics within 15 minutes, 41.8% of peri-urban fringe residents remain completely isolated from pedestrian healthcare.",
    tier4_impact: "Partnered with Ghana's Land Use and Spatial Planning Authority (LUSPA) during the Esri Map4Impact Hackathon (2nd Place) to optimize transit-oriented health post placement.",
    diagram: `Threshold Walk Time   | Mean Catchment Radius | Urban Core Access | Peri-Urban Access
-----------------------+-----------------------+-------------------+------------------
5-Minute Walk (400 m)  | 380 m                 | 62.4%             | 14.1%
10-Minute Walk (800 m) | 760 m                 | 84.1%             | 36.5%
15-Minute Walk (1200 m)| 1,140 m               | 93.8%             | 58.2% (41.8% Deficit!)

NETWORK TOPOLOGY: Nodes: 18,420 | Edges: 42,110 | Mean Circuity Factor: 1.14`,
    github_link: "https://github.com/Emmanuel-Yerbo/GEOAI/tree/main/09_Network_Accessibility_15MinCity"
  }
];

// DOM RENDERING & EVENT HANDLING
document.addEventListener("DOMContentLoaded", () => {
  const projectsGrid = document.getElementById("projectsGrid");
  const filterBtns = document.querySelectorAll(".filter-btn");
  const modal = document.getElementById("projectModal");
  const modalBody = document.getElementById("modalBody");
  const modalClose = document.getElementById("modalClose");
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  // Mobile menu toggle
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
  });

  // Render Project Cards
  function renderProjects(filter = "all") {
    projectsGrid.innerHTML = "";
    const filtered = filter === "all" ? PROJECTS_DATA : PROJECTS_DATA.filter(p => p.category === filter);
    
    filtered.forEach(project => {
      const card = document.createElement("div");
      card.className = "project-card";
      card.onclick = () => openProjectModal(project);

      card.innerHTML = `
        <div class="card-top">
          <span class="project-num">PROJECT ${project.num}</span>
          <span class="project-category">${project.catLabel}</span>
        </div>
        <h3>${project.title}</h3>
        <p class="project-summary">${project.summary}</p>
        <div class="project-badges">
          ${project.tech.map(t => `<span class="tech-badge">${t}</span>`).join("")}
        </div>
        <div class="card-footer-action">
          <span>View 4-Tier Analysis</span>
          <i class="fas fa-arrow-right"></i>
        </div>
      `;
      projectsGrid.appendChild(card);
    });
  }

  // Filter tab clicks
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderProjects(btn.dataset.filter);
    });
  });

  // Open Modal with 4-Tier Breakdown
  window.openProjectModal = function(project) {
    modalBody.innerHTML = `
      <div style="margin-bottom: 1.5rem;">
        <span class="project-num" style="font-size: 1rem;">PROJECT ${project.num} • ${project.catLabel}</span>
        <h2 style="font-size: 1.6rem; margin: 0.4rem 0 0.8rem; line-height: 1.3;">${project.title}</h2>
        <div class="project-badges">
          ${project.tech.map(t => `<span class="tech-badge">${t}</span>`).join("")}
        </div>
      </div>

      <div class="tier-block">
        <div class="tier-label"><i class="fas fa-exclamation-triangle"></i> Tier 1: Spatial Problem</div>
        <div class="tier-text">${project.tier1_problem}</div>
      </div>

      <div class="tier-block">
        <div class="tier-label"><i class="fas fa-project-diagram"></i> Tier 2: Methodological Pipeline</div>
        <div class="tier-text">${project.tier2_pipeline}</div>
      </div>

      <div class="tier-block">
        <div class="tier-label"><i class="fas fa-check-circle"></i> Tier 3: Model Validation & Rigor</div>
        <div class="tier-text">${project.tier3_validation}</div>
      </div>

      <div class="tier-block">
        <div class="tier-label"><i class="fas fa-landmark"></i> Tier 4: Policy & Planning Impact</div>
        <div class="tier-text">${project.tier4_impact}</div>
      </div>

      <h4 style="font-size: 1rem; margin-top: 1.5rem;">Empirical Benchmark & Metrics Matrix</h4>
      <pre class="pre-diagram">${project.diagram}</pre>

      <div style="margin-top: 1.8rem; display: flex; gap: 1rem; flex-wrap: wrap;">
        <a href="${project.github_link}" target="_blank" rel="noopener" class="btn btn-primary">
          <i class="fab fa-github"></i> Inspect Subfolder Code & Notebooks
        </a>
        <button class="btn btn-secondary" onclick="document.getElementById('projectModal').style.display='none'">
          Close View
        </button>
      </div>
    `;
    modal.style.display = "flex";
  };

  // Close Modal
  modalClose.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  // Initial render
  renderProjects("all");
});
