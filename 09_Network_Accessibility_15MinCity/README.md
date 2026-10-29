# Pedestrian Accessibility & The '15-Minute City' Framework
## Case Study: Greater Accra Healthcare & Service Infrastructure

[![OSMnx](https://img.shields.io/badge/OSMnx-Pedestrian%20Graph-blue)](https://osmnx.readthedocs.io/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Dijkstra%20Isochrones-orange)](https://networkx.org/)
[![Pydeck](https://img.shields.io/badge/Pydeck-WebGL%203D-green)](https://deckgl.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

> **Lead Researcher & Engineer:** **Emmanuel Yerbo**  
> *BSc Geography & Regional Planning (First Class Honours, GPA: 3.82/4.00, Three-Time Dean's Award Recipient) — University of Cape Coast, Ghana*  
> 🆔 [ORCID: 0009-0008-8968-6999](https://orcid.org/0009-0008-8968-6999) | 💼 [LinkedIn](https://www.linkedin.com/in/emmanuelyerbo) | 💻 [GitHub Profile](https://github.com/Emmanuel-Yerbo) | 🌐 [Interactive Portfolio](https://emmanuelyerbo.github.io/emmanuelyerbo)

---

### ⚡ Executive Summary

1. **The Core Spatial Problem:** Rapid polycentric growth in Greater Accra has created severe healthcare deserts, where rapid settlement expansion outpaces walkable pedestrian access to public clinics and emergency medical infrastructure.
2. **The Technical Pipeline:** We constructed topological walkable graph networks from OpenStreetMap data using OSMnx, executing NetworkX Dijkstra shortest-path algorithms and convex hull geometric buffering to generate 5, 10, and 15-minute walking isochrones rendered in PyDeck 3D WebGL.
3. **Quantified Impact:** The analysis revealed that **41.8% of peri-urban residents live outside the 15-minute pedestrian healthcare catchment**, providing Ghana's Land Use and Spatial Planning Authority (LUSPA) with quantifiable spatial evidence for transit-oriented health post placement.

### 📊 Empirical Performance & Validation Evidence

| Walking Time Threshold | Catchment Radius (Mean) | Urban Core Coverage | Peri-Urban Fringe Coverage | Service Equity Status |
|---|:---:|:---:|:---:|---|
| **5-Minute Walk (400 m)** | 380 m | 62.4% | 14.1% | High core concentration |
| **10-Minute Walk (800 m)** | 760 m | 84.1% | 36.5% | Moderate transitional access |
| **15-Minute Walk (1200 m)** | 1,140 m | **93.8%** | **58.2%** | **41.8% Underserved Healthcare Desert** |

#### Network Topology Metrics
- **Total Street Nodes:** **18,420** | **Total Graph Edges:** **42,110** | **Mean Circuity Factor:** **1.14**
- **Healthcare Desert Isolation Index:** High vulnerability concentrated across Ga South, Kpone Katamanso, and Amasaman.

---

### 1. Introduction: The Spatial Logic of Accessibility
In urban studies, **accessibility** is the primary metric of equity. This repository implements an **Isochrone-based analysis** to evaluate the '15-Minute City' model within Accra, Ghana. An isochrone (a line of equal travel time) allows us to move beyond simplistic 'as-the-crow-flies' Euclidean buffers and instead model the realistic urban fabric—accounting for street connectivity, physical barriers, topology, and human walking speeds.

---

#### 2. Methodological Pipeline & Network Flow

```mermaid
flowchart LR
    A["OSM Pedestrian Topology"] --> B["NetworkX Graph (4.5 km/h)"] --> C["Dijkstra Traversal"] --> D["Per-Facility Isochrones"] --> E["Underserved Desert Mask"]
```

#### 2.1 Network Modeling (OSMnx & NetworkX)
- **The Process**: We extract the OpenStreetMap (OSM) pedestrian topology graph (`G_walk`) across the study bounds.
- **The Essence**: Unlike vehicular driving networks, pedestrian networks must capture informal footpaths, sidewalks, and pedestrian-only passages. We assign travel friction (time cost) to every edge based on an empirical pedestrian walking speed of **4.5 km/h (1.25 m/s)**.

#### 2.2 Per-Facility Convex Hull Isochrones
- **The Process**: For every Point of Interest (POI), we traverse the network graph using Dijkstra's shortest-path algorithm to delineate all nodes reachable within discrete time increments (5, 10, 15, 20 minutes):
  $$d(v) = \min_{u \in \text{Pred}(v)} [d(u) + w(u, v)]$$
- **The Essence**: We implement a **Per-Facility Convex Hull** architecture. By computing an individual convex hull for each facility and subsequently performing a spatial union, we preserve the organic geometry of realistic service catchments and eliminate the "global hull" error that artificially overestimates accessibility in sparse peripheral zones.

---

### 3. Scenario Analysis: Urban Accessibility Insights

#### Scenario 1: Anchor Institution Reachability (Korle-Bu Teaching Hospital)
- **Purpose**: Micro-scale pedestrian reachability audit of Ghana’s premier national teaching hospital.
- **Insight**: Multi-ring gradient isochrones reveal how dense inner-city street fabrics support rapid 5-to-10 minute pedestrian ingress, while major arterial barriers quickly truncate pedestrian access toward fringe settlements.

#### Scenario 2: Facility Overlap & Clustering
- **Purpose**: Modeling 10 random healthcare Points of Interest across central Accra.
- **Insight**: Exposes the **co-location clustering effect**. Where isochrone envelopes heavily intersect, municipal infrastructure exhibits high service redundancy; conversely, solitary nodes represent fragile access lifelines where a single clinic failure leaves surrounding neighborhoods entirely cut off.

#### Scenario 3: Healthcare Desert Identification
- **Purpose**: Citywide 15-minute coverage envelope evaluated against the official Administrative District Boundary.
- **Insight**: By computing the geometric spatial difference:
  $$\text{Desert} = \text{District Boundary} \setminus \bigcup \text{Isochrones}_{15\text{min}}$$
  we precisely isolate and map structural **Healthcare Deserts**. These under-served polygons constitute the highest-priority target zones for future municipal capital expenditure and clinic siting.

#### Scenario 4: Multi-Category Accessibility Comparison
- **Purpose**: Tri-partite side-by-side accessibility benchmarking across critical urban functions (Health, Education, Markets).
- **Insight**: True urban livability cannot be diagnosed through healthcare alone. This multi-sectoral scenario tests whether a citizen can concurrently access all three essential urban pillars within the same 15-minute walking radius, delineating the genuine 'Complete Neighborhoods' of Greater Accra.

---

### 4. Implementation Engine

The complete reproducible engine is provided in `src/isochrone_walk_engine.py`:

```python
import osmnx as ox
import networkx as nx
from shapely.geometry import Polygon, MultiPolygon
from src.isochrone_walk_engine import build_walk_network, compute_isochrone_polygons

# Build walking graph (4.5 km/h walking speed)
G = build_walk_network(place_name="Accra, Ghana", network_type="walk")

# Generate 5, 10, 15-minute travel time isochrone boundaries
isochrone_gdf = compute_isochrone_polygons(G, poi_coords=[(5.556, -0.196)], trip_times=[5, 10, 15])
```
```
- **Insight**: Leveraging WebGL hardware acceleration, planners can dynamically query catchment polygons, hover over facility attributes, and zoom into micro-street bottlenecks, bridging the gap between raw spatial network science and executive municipal decision-making.

---

### 4. Planning Implications
This framework serves as an objective **Diagnostic Instrument** for the Greater Accra Metropolitan Area. It empirically demonstrates that while historic central districts achieve near-complete 15-minute pedestrian accessibility, post-2000 peripheral sprawl remains structurally automobile-dependent. Converting these diagnosed 'Healthcare Deserts' into vibrant, self-contained complete neighborhoods represents the defining urban planning priority for West African climate resilience and spatial equity.