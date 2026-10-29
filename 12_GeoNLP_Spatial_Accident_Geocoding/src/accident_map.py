"""
accident_map.py
===============
Stage 5: Builds a premium interactive GeoSentiment dashboard map from geocoded data.
Features:
- Dark-mode / Light-mode / Satellite tile layers
- MarkerCluster for individual accident records
- Data-Driven Blackspots Layer (DBSCAN Centroids & Hotspots)
- PRGI Layer (Over-Amplified vs. Silent High-Risk Zones)
- Sentiment HeatMap weighted by Urgency Index
- Blame Attribution Layers (Driver, Infrastructure, Institutional, Vehicle Defect)
- Road Network Graph Topology Layer G(V, E) (Polylines & Traffic Bottlenecks)
- Search Plugin for searching locations directly
- Rich HTML popups with emotion bars, sentiment meters, and blame badges
"""

import csv
import html
import json
import os
from collections import Counter
from typing import List, Dict, Any

import folium
from folium import plugins

from ghana_gazetteer import get_coordinates
from spatial.network_graph import GHANA_ROAD_EDGES, HIGHWAY_COLORS

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "maps")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "reports")

# ── Map Configurations ───────────────────────────────────────────────────
GHANA_CENTER = [7.9465, -1.0232]
ACCRA_CENTER = [5.6037, -0.1870]
KUMASI_CENTER = [6.6885, -1.6244]

SEVERITY_COLORS = {
    "fatal": "red",
    "injury": "orange",
    "property_damage": "beige",
    "unknown": "blue",
}

SEVERITY_ICONS = {
    "fatal": "skull-crossbones",
    "injury": "ambulance",
    "property_damage": "car-crash",
    "unknown": "exclamation-triangle",
}

BLAME_COLORS = {
    "DRIVER": "#e74c3c",          # Red
    "INFRASTRUCTURE": "#e67e22",  # Orange
    "INSTITUTIONAL": "#9b59b6",   # Purple
    "VEHICLE": "#f1c40f",        # Yellow
    "PEDESTRIAN": "#1abc9c",     # Teal
    "SYSTEMIC": "#34495e",       # Dark Blue
    "UNSPECIFIED": "#7f8c8d"     # Gray
}


def load_geocoded_data(filepath: str = None) -> list:
    """Load geocoded accident records."""
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "accidents_geocoded.csv")

    if not os.path.exists(filepath):
        filepath_alt = os.path.join(DATA_DIR, "accidents_extracted.csv")
        if os.path.exists(filepath_alt):
            filepath = filepath_alt
        else:
            print(f"  [!] File not found: {filepath}")
            return []

    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                records.append(row)
            except (ValueError, KeyError, TypeError):
                continue
    return records


def load_blackspots_data() -> list:
    """Load discovered blackspots from report CSV or JSON."""
    csv_path = os.path.join(REPORTS_DIR, "blackspot_summary.csv")
    if not os.path.exists(csv_path):
        return []

    blackspots = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["cluster_id"] = int(row["cluster_id"])
                row["centroid_latitude"] = float(row["centroid_latitude"])
                row["centroid_longitude"] = float(row["centroid_longitude"])
                row["total_incidents"] = int(row["total_incidents"])
                row["fatalities_count"] = int(row["fatalities_count"])
                row["injuries_count"] = int(row["injuries_count"])
                blackspots.append(row)
            except (ValueError, KeyError, TypeError):
                continue
    return blackspots


def load_prgi_data() -> list:
    """Load PRGI gap analysis from report CSV."""
    csv_path = os.path.join(REPORTS_DIR, "prgi_summary.csv")
    if not os.path.exists(csv_path):
        return []

    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["latitude"] = float(row["latitude"])
                row["longitude"] = float(row["longitude"])
                row["prgi_index"] = float(row["prgi_index"])
                records.append(row)
            except (ValueError, KeyError, TypeError):
                continue
    return records


def load_network_graph_data() -> list:
    """Load Road Network Graph topology centrality stats."""
    csv_path = os.path.join(REPORTS_DIR, "network_graph_summary.csv")
    if not os.path.exists(csv_path):
        return []

    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["betweenness_centrality"] = float(row["betweenness_centrality"])
                row["degree_centrality"] = float(row["degree_centrality"])
                row["closeness_centrality"] = float(row["closeness_centrality"])
                records.append(row)
            except (ValueError, KeyError, TypeError):
                continue
    return records


def create_popup_html(record: dict) -> str:
    """Generate rich dark-mode HTML popup for accident markers."""
    title = html.escape(str(record.get("title", "Road Accident Report")))
    loc_name = html.escape(str(record.get("location_name", "Unknown Location")))
    severity = str(record.get("severity", "unknown")).lower()
    vehicle = html.escape(str(record.get("vehicle_types", "Unspecified")))
    blame = html.escape(str(record.get("blame_targets", "Unspecified")))
    url_str = record.get("url", "#")
    source_str = html.escape(str(record.get("source", "News Media")))

    vader_comp = float(record.get("vader_compound", 0.0))
    urgency_idx = float(record.get("urgency_index", 0.5))
    urgency_pct = int(urgency_idx * 100)

    # Emotions
    emotions = {
        "Fear": float(record.get("emo_fear", 0)),
        "Sadness": float(record.get("emo_sadness", 0)),
        "Anger": float(record.get("emo_anger", 0)),
        "Shock": float(record.get("emo_shock", 0)),
        "Urgency": float(record.get("emo_urgency", 0)),
    }
    dominant_emo = max(emotions, key=emotions.get) if any(emotions.values()) else "Neutral"

    # Polarity Badge
    if vader_comp <= -0.5:
        polarity_badge = '<span style="background:#e74c3c; color:white; padding:2px 6px; border-radius:3px; font-size:10px;">🔴 Highly Negative</span>'
    elif vader_comp < 0.0:
        polarity_badge = '<span style="background:#e67e22; color:white; padding:2px 6px; border-radius:3px; font-size:10px;">🟠 Negative</span>'
    else:
        polarity_badge = '<span style="background:#2ecc71; color:white; padding:2px 6px; border-radius:3px; font-size:10px;">🟢 Neutral/Positive</span>'

    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 280px; padding: 12px; background: #0f111a; color: #e0e6ed; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <div style="border-bottom: 2px solid #30363d; padding-bottom: 6px; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #ff5252; font-size: 14px; font-weight: 700;">📍 {loc_name}</h4>
            <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">{title[:50]}...</div>
        </div>

        <div style="font-size: 11px; line-height: 1.6; margin-bottom: 10px;">
            <div>🚨 <strong>Severity:</strong> <span style="text-transform: capitalize; color: #ffb74d;">{severity}</span></div>
            <div>🚗 <strong>Vehicles:</strong> <span style="color: #64b5f6;">{vehicle}</span></div>
        </div>

        <!-- Sentiment & Urgency Meter -->
        <div style="background: #1e1e30; padding: 8px; border-radius: 6px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 11px;">
                <span>Tone: {polarity_badge}</span>
                <span>Emotion: <strong style="color:#ffb74d;">{dominant_emo}</strong></span>
            </div>
            <div style="margin-top: 6px;">
                <div style="display:flex; justify-content:space-between; font-size:10px; color:#aaa; margin-bottom:2px;">
                    <span>Urgency / Panic Index:</span>
                    <span>{urgency_pct}%</span>
                </div>
                <div style="width: 100%; background: #333; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="width: {urgency_pct}%; background: linear-gradient(90deg, #ff9800, #f44336); height: 100%;"></div>
                </div>
            </div>
        </div>

        <!-- Blame Attribution -->
        <div style="font-size: 11px; margin-bottom: 10px; background: #1a237e; padding: 6px 8px; border-radius: 4px;">
            🎯 <strong>Blame Attribution:</strong> <span style="color: #90caf9;">{blame}</span>
        </div>

        <div style="font-size: 10px; color: #888; text-align: right;">
            Source: <a href="{url_str}" target="_blank" style="color: #4fc3f7; text-decoration: none;">{source_str} 🔗</a>
        </div>
    </div>
    """


def build_map(records: list, center: str = "ghana", output_path: str = None) -> str:
    """Build the multi-layer GeoSentiment interactive Folium map."""
    if not records:
        print("  [!] No records to plot on map.")
        return None

    if output_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, "ghana_accident_map.html")

    # Determine center
    centers = {
        "ghana": GHANA_CENTER,
        "accra": ACCRA_CENTER,
        "kumasi": KUMASI_CENTER,
    }
    map_center = centers.get(center.lower(), GHANA_CENTER)

    print(f"\n  Building GeoSentiment Map ({len(records)} markers)...")

    # Create base map with CartoDB Dark_Matter default for rich aesthetics
    m = folium.Map(
        location=map_center,
        zoom_start=7 if center == "ghana" else 12,
        tiles="CartoDB dark_matter",
        name="🌙 Dark Mode (Default)",
    )

    # Additional base tiles
    folium.TileLayer("OpenStreetMap", name="🗺️ Street View").add_to(m)
    folium.TileLayer("CartoDB positron", name="☀️ Light Mode").add_to(m)

    # ── Layer 1: Data-Driven Blackspots (DBSCAN Clusters) ──────────────────
    blackspots = load_blackspots_data()
    blackspot_fg = folium.FeatureGroup(name="📍 Data-Driven Blackspots (DBSCAN)", show=True).add_to(m)

    for bs in blackspots:
        c_lat, c_lon = bs["centroid_latitude"], bs["centroid_longitude"]
        total_inc = bs["total_incidents"]
        fatalities = bs["fatalities_count"]
        injuries = bs["injuries_count"]
        primary_loc = html.escape(bs["primary_location"])
        vehicle = html.escape(bs["predominant_vehicle"])
        blame = html.escape(bs["predominant_blame"])

        circle_radius = min(15 + (total_inc * 3), 45)

        popup_html = f"""
        <div style="font-family:'Segoe UI',sans-serif; width:260px; padding:10px; background:#0d1117; color:#c9d1d9; border-radius:6px; border:1px solid #30363d;">
            <div style="background:#da3633; color:white; padding:4px 8px; font-weight:bold; font-size:12px; border-radius:4px; margin-bottom:8px;">
                🚨 BLACKSPOT CLUSTER #{bs['cluster_id']}
            </div>
            <h4 style="margin:0 0 6px 0; color:#58a6ff;">📍 {primary_loc} Corridor</h4>
            <div style="font-size:11px; line-height:1.6;">
                • <strong>Total Accidents:</strong> {total_inc}<br>
                • <strong>Fatalities:</strong> <span style="color:#f85149;">{fatalities}</span> | <strong>Injuries:</strong> <span style="color:#e3b341;">{injuries}</span><br>
                • <strong>Predominant Vehicle:</strong> <span style="color:#79c0ff;">{vehicle}</span><br>
                • <strong>Primary Blame:</strong> <span style="color:#d2a8ff;">{blame}</span>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[c_lat, c_lon],
            radius=circle_radius,
            color="#ff4444",
            fill=True,
            fill_color="#ff1111",
            fill_opacity=0.45,
            weight=3,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"🚨 Blackspot: {primary_loc} ({total_inc} incidents)",
        ).add_to(blackspot_fg)

    # ── Layer 2: PRGI Gap Analysis Layer ──────────────────────────────────
    prgi_records = load_prgi_data()
    prgi_fg = folium.FeatureGroup(name="⚖️ Perception-Reality Gap (PRGI)", show=False).add_to(m)

    for pr in prgi_records:
        p_lat, p_lon = pr["latitude"], pr["longitude"]
        status = pr["prgi_status"]
        prgi_val = pr["prgi_index"]
        loc = html.escape(pr["location_name"])

        if status == "Over-Amplified Zone":
            p_color = "#e74c3c"
        elif status == "Silent High-Risk Zone":
            p_color = "#3498db"
        else:
            p_color = "#2ecc71"

        prgi_popup = f"""
        <div style="font-family:'Segoe UI',sans-serif; width:240px; padding:10px; background:#1e1e2e; color:#fff; border-radius:6px;">
            <h4 style="margin:0 0 6px 0; color:#89b4fa;">📍 {loc}</h4>
            <div style="font-size:11px; line-height:1.5;">
                • <strong>PRGI Index:</strong> <span style="color:#f9e2af; font-size:13px; font-weight:bold;">{prgi_val}</span><br>
                • <strong>Category:</strong> <span style="color:{p_color}; font-weight:bold;">{status}</span><br>
                • <strong>Incidents:</strong> {pr['incidents_count']}<br>
                • <strong>Fatalities:</strong> {pr['fatalities_count']}<br>
                • <strong>Perception Score:</strong> {pr['perception_score']}<br>
                • <strong>Reality Score:</strong> {pr['reality_score']}
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[p_lat, p_lon],
            radius=9,
            color=p_color,
            fill=True,
            fill_color=p_color,
            fill_opacity=0.8,
            popup=folium.Popup(prgi_popup, max_width=280),
            tooltip=f"PRGI {prgi_val}: {loc} ({status})",
        ).add_to(prgi_fg)

    # ── Layer 3: Road Network Graph Topology G(V, E) ───────────────────────
    net_fg = folium.FeatureGroup(name="🛣️ Road Network Topology G(V, E)", show=False).add_to(m)
    net_data = load_network_graph_data()
    net_lookup = {r["location_name"]: r for r in net_data}

    # Add Highway Edges Polylines
    for u, v, weight, h_code in GHANA_ROAD_EDGES:
        c1 = get_coordinates(u)
        c2 = get_coordinates(v)
        if c1 and c2:
            h_color = HIGHWAY_COLORS.get(h_code, "#888888")
            folium.PolyLine(
                locations=[[c1[0], c1[1]], [c2[0], c2[1]]],
                color=h_color,
                weight=4,
                opacity=0.8,
                tooltip=f"🛣️ {h_code} Corridor: {u} ↔ {v} ({weight} km)"
            ).add_to(net_fg)

    # Add Network Bottleneck Nodes
    for loc_name, n_info in net_lookup.items():
        c = get_coordinates(loc_name)
        if c:
            b_val = n_info["betweenness_centrality"]
            c_val = n_info["closeness_centrality"]
            d_val = n_info["degree_centrality"]
            node_rad = max(6, int(b_val * 40))

            net_popup = f"""
            <div style="font-family:'Segoe UI',sans-serif; width:250px; padding:10px; background:#0d1117; color:#00e676; border-radius:6px; border:1px solid #00e676;">
                <h4 style="margin:0 0 6px 0; color:#fff;">🛣️ Node: {html.escape(loc_name)}</h4>
                <div style="font-size:11px; line-height:1.6; color:#c9d1d9;">
                    • <strong>Betweenness (C_b):</strong> <span style="color:#00e676; font-weight:bold;">{b_val}</span><br>
                    • <strong>Closeness (C_c):</strong> {c_val}<br>
                    • <strong>Degree (C_d):</strong> {d_val}<br>
                    • <strong>Connected Arterials:</strong> {n_info['connected_arterials']}
                </div>
            </div>
            """

            folium.CircleMarker(
                location=[c[0], c[1]],
                radius=node_rad,
                color="#00e676",
                fill=True,
                fill_color="#00e676",
                fill_opacity=0.85,
                popup=folium.Popup(net_popup, max_width=280),
                tooltip=f"🛣️ Bottleneck Node: {loc_name} (C_b = {b_val})",
            ).add_to(net_fg)

    # ── Layer 4: MarkerCluster for Individual Incidents ──────────────────
    marker_cluster = plugins.MarkerCluster(
        name="📍 All Incident Markers",
        show=True,
        options={"chunkedLoading": True, "maxClusterRadius": 50},
    ).add_to(m)

    heat_data = []
    popup_cache = {}

    for r in records:
        lat, lon = r["latitude"], r["longitude"]
        severity = r.get("severity", "unknown")
        color = SEVERITY_COLORS.get(severity, "blue")
        icon_name = SEVERITY_ICONS.get(severity, "exclamation-triangle")

        urgency_val = float(r.get("urgency_index", 0.5))
        heat_data.append([lat, lon, urgency_val])

        popup_html = create_popup_html(r)
        popup_cache[id(r)] = popup_html

        marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{html.escape(r.get('location_name', 'Unknown'))} ({severity})",
            icon=folium.Icon(
                color=color,
                icon=icon_name,
                prefix="fa",
            ),
        )
        marker.add_to(marker_cluster)

    # ── Layer 5: Sentiment Panic Heatmap ────────────────────────────────
    if heat_data:
        plugins.HeatMap(
            heat_data,
            name="🔥 Panic & Urgency Heatmap",
            show=False,
            radius=25,
            blur=15,
            gradient={0.2: "blue", 0.4: "cyan", 0.6: "lime", 0.8: "yellow", 1.0: "red"},
        ).add_to(m)

    # ── Layer 6: Blame Attribution Overlays ──────────────────────────────
    blame_fg_driver = folium.FeatureGroup(name="🚗 Blame: Driver Recklessness", show=False).add_to(m)
    blame_fg_infra = folium.FeatureGroup(name="🛣️ Blame: Infrastructure & Roads", show=False).add_to(m)
    blame_fg_veh = folium.FeatureGroup(name="🚛 Blame: Vehicle Defects", show=False).add_to(m)

    for r in records:
        blame_str = str(r.get("blame_targets", ""))
        popup_html = popup_cache.get(id(r), create_popup_html(r))
        lat, lon = r["latitude"], r["longitude"]

        if "DRIVER" in blame_str:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color="#e74c3c",
                fill=True,
                fill_color="#e74c3c",
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=f"Driver Blame: {r.get('location_name', 'Unknown')}",
            ).add_to(blame_fg_driver)

        if "INFRASTRUCTURE" in blame_str:
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color="#e67e22",
                fill=True,
                fill_color="#e67e22",
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=f"Infra Blame: {r.get('location_name', 'Unknown')}",
            ).add_to(blame_fg_infra)

        if "VEHICLE" in blame_str:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color="#f1c40f",
                fill=True,
                fill_color="#f1c40f",
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=f"Vehicle Blame: {r.get('location_name', 'Unknown')}",
            ).add_to(blame_fg_veh)

    # Search Plugin
    plugins.Search(
        layer=marker_cluster,
        geom_type="Point",
        placeholder="Search location (e.g. Accra, Kumasi, Gomoa Okyereko)...",
        collapsed=False,
        search_label="tooltip",
    ).add_to(m)

    # Layer Control
    folium.LayerControl(collapsed=False).add_to(m)

    # Save HTML
    m.save(output_path)

    print(f"\n{'='*60}")
    print(f"  GEOSENTIMENT DASHBOARD MAP GENERATED WITH ROAD NETWORK LAYER")
    print(f"  File: {output_path}")
    print(f"{'='*60}")

    return output_path


if __name__ == "__main__":
    records = load_geocoded_data()
    if records:
        build_map(records)
    else:
        print("  [!] No geocoded records found to build map.")
