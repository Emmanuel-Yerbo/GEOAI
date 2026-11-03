# 🏙️ Multi-Temporal Explainable AI (XAI) for Land Use & Land Cover (LULC) Classification
## Empirical Tree SHAP Game Attribution & Rapid Urban Expansion in Greater Accra (GAMA), Ghana (2020–2024)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7+-green?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Tree SHAP](https://img.shields.io/badge/Explainability-Tree%20SHAP%20Game%20Theory-blue)](https://shap.readthedocs.io/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-Sentinel--2%20MSI-34A853?logo=google-earth&logoColor=white)](https://earthengine.google.com/)
[![Geography: GAMA Accra](https://img.shields.io/badge/Geography-Greater%20Accra%20(GAMA)%2C%20Ghana-gold)]()
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen)](https://github.com/Emmanuel-Yerbo/GEOAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Author & Research Engineer:** **Emmanuel Yerbo**  
> *Department of Geography and Regional Planning, University of Cape Coast (UCC), Ghana*  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient)*  
> 🔬 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

## 📌 Executive Summary

The **Greater Accra Metropolitan Area (GAMA)** represents one of West Africa's fastest-growing urban corridors, characterized by aggressive peri-urban expansion, wetland degradation (Korle and Sakumo Lagoons), and severe loss of agricultural and coastal ecological buffers. Accurate, multi-temporal Land Use and Land Cover (LULC) tracking is critical for sustainable urban governance, flood mitigation, and regional planning.

However, standard machine learning classifiers operate as uninterpretable "black boxes," leaving urban planners and environmental scientists unable to verify *why* specific land parcels are categorized into built-up fabric or bare soil.

This project delivers an end-to-end **Multi-Temporal Explainable AI (XAI) Pipeline** across GAMA across three milestone years: **2020**, **2022**, and **2024**. Integrating Google Earth Engine (GEE) cloud ETL with an advanced machine learning suite (**Extreme Gradient Boosting / XGBoost**, **Random Forest / RF**, and **Support Vector Machine / SVM**), the framework benchmarks models on a **25-band multi-modal feature stack** (Sentinel-2 multi-spectral bands, biophysical indices, GLCM spatial textures, and SRTM elevation derivatives). It rigorously controls for multicollinearity via Pearson correlation pruning ($|r| > 0.95$), and applies **Tree SHAP (SHapley Additive exPlanations)** cooperative game theory to unlock pixel-level, per-class, and global feature attributions.

---

## 🗺️ Multi-Temporal Urban Sprawl in Greater Accra (2020 $\to$ 2024)

<p align="center">
  <img src="results/lulc_classification_map.jpg" width="48%" alt="LULC Baseline Classification GAMA">
  &nbsp;&nbsp;
  <img src="results/lulc_2022_map.jpg" width="48%" alt="LULC Multi-Temporal Monitoring GAMA">
  <br>
  <em><b>Figure 1:</b> Multi-temporal LULC spatial zonation across the Greater Accra Metropolitan Area (GAMA, 3,734.77 km², 13,440 × 7,040 pixels): Baseline classification (left) versus multi-temporal monitoring (right) capturing massive westward (Ga South / Kasoa) and northward (Ga West / Adenta-Dodowa) urban built-up expansion.</em>
</p>

---

## 🏗️ 6-Stage Engineering Matrix

| Stage | Pipeline Phase | Core Engine & Mathematical Formulation | Scientific Role & Operational Purpose | Output Artifact / Tensor |
|:---:|---|---|---|---|
| **01** | **Multi-Temporal EO Harmonization** | GEE Sentinel-2 SR Harmonized (`COPERNICUS/S2_SR_HARMONIZED`) | Ingest BOA surface reflectance across 2020, 2022, 2024; mask clouds via QA60 cirrus/cloud bits; compute 15th-percentile composite (darkest clean pixels). | Annual cloud-free surface rasters ($10\text{ m}$) |
| **02** | **25-Band Multi-Modal Stacking** | Multi-sensor feature stacker: 10 spectral + 7 indices + 5 GLCM + 2 terrain | Concatenate raw bands ($B_2 \dots B_{12}$), spectral indices (NDVI, MNDWI, NDBI, BSI, EVI, SAVI, NDWI), GLCM spatial textures (entropy, contrast, correlation, homogeneity, ASM), and SRTM elevation/slope. | 25-Channel observation tensor ($\mathbf{X} \in \mathbb{R}^{H \times W \times 25}$) |
| **03** | **Multicollinearity Pruning** | Pearson correlation $|r_{jk}| > 0.95$, dropping redundant collinear pairs | Eliminates multicollinearity that corrupts Shapley value attributions, reducing the feature space from 24 input features to 14 orthogonal biophysical drivers. | Pruned orthogonal feature matrix $\mathbf{X}^* \in \mathbb{R}^{N \times 14}$ |
| **04** | **Supervised Model Benchmark** | Stratified train/test validation across XGBoost, Random Forest, and SVM | Trains non-linear ensemble models to categorize pixels into Built-Up (`#E8453C`), Vegetation (`#1B7A2F`), Water (`#2196F3`), and Bare Soil (`#9E9E9E`). | Trained model ensembles, confusion matrices, Cohen's $\kappa$ |
| **05** | **Tree SHAP Game Attribution** | TreeExplainer cooperative game theory: $\phi_i(x) = \sum \frac{|S|!(|F|-|S|-1)!}{|F|!}[f_x(S \cup \{i\}) - f_x(S)]$ | Computes exact marginal contributions per feature for every prediction, generating global feature importance, local force plots, and class-specific marginal profiles. | Pixel-level Shapley attribution matrix $\mathbf{\Phi} \in \mathbb{R}^{N \times 14}$ |
| **06** | **Full-Scene Multi-Year Inference** | Block streaming $(13,440 \times 7,040\text{ px})$, TFRecord export | Generates full-coverage annual LULC GeoTIFFs, computing pixel census class transitions and net hectares converted to urban fabric. | Annual LULC GeoTIFFs & sprawl transition matrix |

---

## 🔬 Mathematical & Game-Theoretic Formulation

### 1. Multicollinearity Control via Pearson Correlation
In cooperative game theory, Shapley values distribute credit among features based on marginal contributions across all possible subsets $S \subseteq F$. Severe multicollinearity between spectral bands (e.g., $B_8$ vs $B_{8A}$, $r = 0.9936$) creates artificial feature coalitions that split and distort true attribution weights. We compute the bivariate Pearson correlation:
$$r_{jk} = \frac{\sum_{i=1}^N (x_{ij} - \bar{x}_j)(x_{ik} - \bar{x}_k)}{\sqrt{\sum_{i=1}^N (x_{ij} - \bar{x}_j)^2 \sum_{i=1}^N (x_{ik} - \bar{x}_k)^2}}$$
Features exceeding $|r_{jk}| > 0.95$ are systematically pruned:
* **Blue ($B_2$)** dropped ($r = 0.9560$ with Green $B_3$) $\to$ **$B_3$ retained**.
* **RedEdge-1 ($B_5$)** dropped ($r = 0.9539$ with Red $B_4$) $\to$ **$B_4$ retained**.
* **RedEdge-2 ($B_6$), RedEdge-3 ($B_7$), Narrow NIR ($B_{8A}$)** dropped ($r > 0.978$ with NIR $B_8$) $\to$ **$B_8$ retained**.
* **SWIR-2 ($B_{12}$)** dropped ($r = 0.9646$ with SWIR-1 $B_{11}$) $\to$ **$B_{11}$ retained**.
* **EVI, SAVI** dropped ($r > 0.967$ with NDVI) $\to$ **NDVI retained**.
* **NDWI** dropped ($r = -0.9520$ with NDVI) $\to$ **MNDWI retained** (superior for urban wetlands).
* **GLCM_ASM** dropped ($r = -0.9708$ with GLCM_Entropy) $\to$ **GLCM_Entropy retained**.

### 2. Exact Tree SHAP Formulation
For any given pixel with feature vector $\mathbf{x}$, the Shapley value $\phi_i(x)$ of feature $i \in F$ is computed as:
$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|! \; (|F| - |S| - 1)!}{|F|!} \Big[ f_x(S \cup \{i\}) - f_x(S) \Big]$$
where $F$ is the set of 14 orthogonal features, $S$ represents a coalition of features excluding $i$, and $f_x(S) = \mathbb{E}[f(X) \mid X_S = x_S]$ is the conditional expectation of model prediction given subset $S$.

Tree SHAP satisfies the three canonical game-theoretic axioms:
1. **Efficiency (Local Accuracy):** $\sum_{i=1}^{|F|} \phi_i(x) = f(x) - \mathbb{E}[f(X)]$. The sum of all feature attributions equals the difference between the model output and the expected base rate.
2. **Missingness:** If a feature has no impact on the tree path, its Shapley value is identically zero: $x_i = \emptyset \implies \phi_i = 0$.
3. **Consistency:** If a model changes such that the marginal contribution of feature $i$ increases or stays the same, its Shapley value never decreases.

---

## 📊 Empirical Performance & Validation Across Epochs

### Model Comparison Across Epochs (GAMA Test Folds)

| Year | Classifier | Overall Accuracy ($OA$) | Cohen's Kappa ($\kappa$) | Weighted F1-Score | Selected Operational Model |
|:---:|---|:---:|:---:|:---:|:---:|
| **2020** | **Random Forest** | **99.17%** | **0.9889** | **0.9916** | **Ensemble Benchmark Winner** |
| 2020 | Support Vector Machine (SVM) | 98.33% | 0.9778 | 0.9833 | RBF Kernel |
| 2020 | XGBoost | **99.17%** | **0.9889** | **0.9916** | Gradient Boosted Trees |
| **2022** | Random Forest | 98.75% | 0.9833 | 0.9875 | Ensemble Benchmark |
| 2022 | Support Vector Machine (SVM) | 97.92% | 0.9722 | 0.9791 | RBF Kernel |
| 2022 | **XGBoost** | **99.17%** | **0.9889** | **0.9916** | **Operational SHAP Model** |
| **2024** | Random Forest | 98.75% | 0.9833 | 0.9875 | Ensemble Benchmark |
| 2024 | Support Vector Machine (SVM) | 98.33% | 0.9778 | 0.9833 | RBF Kernel |
| 2024 | **XGBoost** | **99.17%** | **0.9889** | **0.9916** | **Operational SHAP Model** |

### Detailed Test Set Classification Report (2024 - Operational Model)

| Land Cover Class | Precision | Recall | F1-Score | Test Support | Dominant Biophysical Identifier |
|---|:---:|:---:|:---:|:---:|---|
| **Built-Up Fabric** | 0.9500 | 0.9833 | 0.9664 | 60 | High NDBI, elevated GLCM Entropy, low NDVI |
| **Vegetation** | **1.0000** | **1.0000** | **1.0000** | 60 | High NIR ($B_8$), peak NDVI ($> 0.60$), low Bare Soil Index |
| **Water Bodies** | **1.0000** | **1.0000** | **1.0000** | 60 | Peak MNDWI, total SWIR-1 ($B_{11}$) absorption, low elevation |
| **Bare Soil** | 0.9831 | 0.9667 | 0.9748 | 60 | High Bare Soil Index (BSI), moderate Red ($B_4$), low GLCM Entropy |
| **Summary / Overall** | **0.9833** | **0.9875** | **0.9853** | **240** | **Overall Accuracy: 99.17%** |

---

## 📈 Quantitative Urban Transition Analysis: Greater Accra (2020–2024)

By performing full-coverage inference across the entire $13,440 \times 7,040$ pixel footprint ($3,734.77\text{ km}^2$) of the Greater Accra Metropolitan Area, the pipeline reveals the alarming magnitude of rapid urban expansion:

```text
========================================================================================================
                      GAMA MULTI-TEMPORAL LULC TRANSITION METRICS (2020 - 2024)
========================================================================================================
 Class           | 2020 Area (km²) | 2020 Share | 2022 Area (km²) | 2022 Share | 2024 Area (km²) | 2024 Share | 4-Year Net Shift
-----------------|-----------------|------------|-----------------|------------|-----------------|------------|------------------
 Built-Up Fabric | 1,696.45 km²    | 45.4%      | 1,848.71 km²    | 49.5%      | 2,229.81 km²    | 59.7%      | +533.36 km² (+31.4%)
 Vegetation      | 1,293.84 km²    | 34.6%      | 1,185.17 km²    | 31.7%      |   817.53 km²    | 21.9%      | -476.31 km² (-36.8%)
 Water Bodies    |   149.57 km²    |  4.0%      |   271.26 km²    |  7.3%      |   152.90 km²    |  4.1%      |   +3.33 km² (+2.2%)
 Bare Soil       |   594.91 km²    | 15.9%      |   429.61 km²    | 11.5%      |   534.51 km²    | 14.3%      |  -60.40 km² (-10.2%)
========================================================================================================
 Total Scene     | 3,734.77 km²    | 100.0%     | 3,734.77 km²    | 100.0%     | 3,734.77 km²    | 100.0%     | 100% Balanced
========================================================================================================
```

> [!IMPORTANT]
> **Key Geospatial Findings for Greater Accra:**  
> 1. **Runaway Urban Sprawl:** Built-up urban fabric exploded from **45.4% ($1,696.45\text{ km}^2$)** in 2020 to **59.7% ($2,229.81\text{ km}^2$)** in 2024. This represents a net conversion of **$533.36\text{ km}^2$** into concrete, roofings, and paved infrastructure in just 4 years (+133.3 km²/year).  
> 2. **Vegetation Depletion:** Over **$476.31\text{ km}^2$ of tree canopy, coastal scrub, and agricultural peri-urban greenbelt** were permanently cleared, with vegetated cover shrinking from **34.6% to 21.9%**.  
> 3. **Wetland & Coastal Buffer Encroachment:** Water body extent fluctuated between 4.0% and 7.3% due to seasonal flooding and tidal variations, but lagoons (Korle, Chemu, Kpeshie) showed progressive edge encroaching by informal and commercial infilling.

---

## 🔬 Biophysical Feature Attribution & Diagnostic Insights

<p align="center">
  <img src="results/feature_importance.png" width="48%" alt="Global Feature Importance">
  &nbsp;&nbsp;
  <img src="results/radar_producer_user_accuracies.png" width="48%" alt="Radar Accuracy Distribution">
  <br>
  <em><b>Figure 2 & 3:</b> Global biophysical feature ranking and per-class classification reliability. <b>Left:</b> Global feature ranking proving that NIR ($B_8$), Elevation, Bare Soil Index (BSI), and Red ($B_4$) dominate decision boundaries. <b>Right:</b> Radar plot comparing Producer's Recall and User's Precision across land categories.</em>
</p>

### Local Decision Attribution: The SHAP Force Plot

<p align="center">
  <img src="results/shap_force_plot.png" width="900" alt="SHAP Force Plot">
  <br>
  <em><b>Figure 4:</b> Pixel-level SHAP force plot illustrating the push-and-pull dynamics of individual spectral features for a single sample: High NDBI and low NDVI push the model prediction toward Built-Up, while moderate slope and elevation provide stabilizing counter-forces.</em>
</p>

---

## 📈 Class-Specific Marginal Response Profiles

<p align="center">
  <img src="results/builtup_profile.png" width="31%" alt="Built-up Marginal Profile">
  &nbsp;
  <img src="results/bare_soil_profile.png" width="31%" alt="Bare Soil Marginal Profile">
  &nbsp;
  <img src="results/water_profile.png" width="31%" alt="Water Marginal Profile">
  <br>
  <em><b>Figure 5:</b> Distinct marginal response profiles across contrasting landscape targets in Greater Accra (Built-up, Bare Soil, and Surface Water).</em>
</p>

### Global Feature Contribution Decomposition

<p align="center">
  <img src="results/shap_global_feature_importance.jpg" width="850" alt="Global SHAP Decomposition">
  <br>
  <em><b>Figure 6:</b> Per-class SHAP contribution scores decomposed across Sentinel-2 surface reflectance, biophysical indices (NDVI, MNDWI, NDBI, BSI), topographic elevation derivatives, and GLCM spatial textures.</em>
</p>

> [!NOTE]
> **Mechanistic Interpretability Takeaways:**  
> 1. **Vegetation Isolation:** Overwhelmingly governed by Near-Infrared ($B_8$, $>15.1\%$ importance) and NDVI, reflecting the steep Red-Edge jump and high chlorophyll reflectance of healthy canopies.  
> 2. **Surface Water Discrimination:** Decisively separated by Modified Normalized Difference Water Index (MNDWI) and SWIR-1 ($B_{11}$), leveraging water's total absorption in shortwave infrared wavelengths.  
> 3. **Built-Up vs. Bare Soil Disambiguation:** Resolving the infamous urban fringe confusion between unpaved laterite roads and concrete structures is achieved through **Bare Soil Index (BSI)** and **GLCM Spatial Texture Entropy**—built-up areas exhibit high local textural heterogeneity, whereas bare soil patches remain texturally uniform.

---

## 📂 Repository Architecture

```text
05_Vision_Transformer_LULC/
├── README.md                                  <-- Publication-grade technical report (You are here)
├── requirements.txt                           <-- Python dependencies (XGBoost, SHAP, Scikit-Learn, Rasterio)
├── data/
│   └── XAI_TRAINING_DATASET.csv               <-- Ground-truth 25-feature training dataset across GAMA
├── scripts/
│   └── gee_xai_lulc_multitemporal.js          <-- GEE cloud pipeline: cloud masking, 15th-percentile composite, feature export
├── notebooks/
│   ├── XGBoost_SHAP_LULC_Pipeline.ipynb       <-- Complete multi-model training & Tree SHAP explainability notebook
│   └── MultiYear_LULC_Evaluation.ipynb        <-- Multi-temporal (2020-2024) full-scene spatial evaluation & area shifts
├── src/
│   ├── __init__.py                            <-- Package entry point
│   ├── dataset.py                             <-- Data loader, label indexing & multicollinearity pruning (|r| > 0.95)
│   ├── train.py                               <-- Multi-model training benchmark (XGBoost, RF, SVM) & classification reports
│   └── explain.py                             <-- Tree SHAP explainability & feature importance attribution engine
└── results/
    ├── lulc_classification_map.jpg            <-- Baseline LULC spatial classification of GAMA (129.4 KB)
    ├── lulc_2022_map.jpg                      <-- Multi-temporal monitoring classification of GAMA (136.0 KB)
    ├── feature_importance.png                 <-- Global feature importance ranking (48.2 KB)
    ├── model_confusion_matrix.png             <-- Confusion matrix across land cover classes (41.3 KB)
    ├── radar_producer_user_accuracies.png     <-- Producer's vs. User's accuracy radar plot (84.8 KB)
    ├── shap_force_plot.png                    <-- Local pixel-level SHAP force plot (52.2 KB)
    ├── builtup_profile.png                    <-- Marginal response curve: Built-up fabric (179.1 KB)
    ├── bare_soil_profile.png                  <-- Marginal response curve: Bare soil (51.7 KB)
    ├── water_profile.png                      <-- Marginal response curve: Surface water (54.1 KB)
    └── shap_global_feature_importance.jpg     <-- Decomposed per-class SHAP contribution scores (69.5 KB)
```

---

## ⚡ Quickstart & Reproducibility

### 1. Environment Installation
```bash
# Navigate to repository directory
cd 05_Vision_Transformer_LULC

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute Model Training & Multi-Model Benchmark
Run the automated pipeline to prune collinear features and evaluate Random Forest, SVM, and XGBoost:
```bash
python src/train.py --data data/XAI_TRAINING_DATASET.csv --test_size 0.20
```

### 3. Compute Tree SHAP Explainability & Feature Rankings
Extract exact Shapley attributions across all land cover targets:
```bash
python src/explain.py --data data/XAI_TRAINING_DATASET.csv
```

### 4. Interactive Jupyter Notebooks
Launch the interactive notebooks to inspect full-scene spatial predictions and generate SHAP summary and force plots:
```bash
jupyter notebook notebooks/XGBoost_SHAP_LULC_Pipeline.ipynb
jupyter notebook notebooks/MultiYear_LULC_Evaluation.ipynb
```

---

## 🏛️ Policy & Spatial Planning Implications for Greater Accra

1. **Defensible Urban Growth Containment:** By providing auditable, game-theoretic feature attributions rather than opaque neural predictions, municipal physical planning departments (e.g., AMA, Ga South, Kpone Katamanso) can legally substantiate zoning violations and building moratoriums in flood-prone buffer zones.
2. **Wetland Reclamation & Flood Defense:** The documented $+533.36\text{ km}^2$ built-up expansion directly correlates with catastrophic seasonal flash flooding along the Odaw River basin. Transparent LULC tracking enables NADMO and the Ministry of Works and Housing to prioritize retention basins where permeable vegetation cover has dropped below critical thresholds.
3. **Frugal Cloud-to-Edge Deployment:** Harmonizing Google Earth Engine for cloud-based composite generation with lightweight gradient-boosted trees allows district assemblies across Ghana to execute annual urban monitoring on standard workstation hardware without expensive supercomputing infrastructure.

---

## 📖 Citation

If you utilize this multi-temporal dataset, feature pruning stack, or Tree SHAP explainability framework in your research, please cite:

```bibtex
@article{yerbo2026xai_gama,
  title     = {Multi-Temporal Explainable AI (XAI) for Land Use and Land Cover 
               Classification: Empirical Tree SHAP Game Attribution and Rapid 
               Urban Expansion in Greater Accra (GAMA), Ghana (2020--2024)},
  author    = {Yerbo, Emmanuel},
  journal   = {Department of Geography and Regional Planning, University of Cape Coast},
  year      = {2026},
  address   = {Cape Coast, Ghana},
  institution = {University of Cape Coast, Ghana},
  orcid     = {0009-0008-8968-6999}
}
```
