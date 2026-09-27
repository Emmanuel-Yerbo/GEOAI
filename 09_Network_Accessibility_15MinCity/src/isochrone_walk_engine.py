"""
Isochrone Walking Network Engine
Author: Emmanuel Yerbo
Implements Dijkstra per-facility convex hull isochrones using OSMnx and NetworkX.
"""
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

def build_pedestrian_graph(place_name="Greater Accra, Ghana", walking_speed_kmh=4.5):
    """
    Fetches walkable network and computes travel times based on pedestrian speeds.
    4.5 km/h = 1.25 m/s.
    """
    G = ox.graph_from_place(place_name, network_type="walk")
    speed_mps = walking_speed_kmh * 1000 / 3600
    for u, v, k, data in G.edges(keys=True, data=True):
        data["time"] = data["length"] / speed_mps
    return G

def compute_per_facility_isochrones(G, facility_points_gdf, trip_times_minutes=[5, 10, 15, 20]):
    """
    Traverses the graph using Dijkstra's algorithm to compute per-facility convex hulls,
    avoiding global hull overestimation in sparse areas.
    """
    isochrone_polys = {t: [] for t in trip_times_minutes}
    
    for idx, row in facility_points_gdf.iterrows():
        nearest_node = ox.distance.nearest_nodes(G, row.geometry.x, row.geometry.y)
        for trip_time in trip_times_minutes:
            subgraph = nx.ego_graph(G, nearest_node, radius=trip_time * 60, distance="time")
            node_points = [Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)]
            if len(node_points) >= 3:
                hull = MultiPoint(node_points).convex_hull
                isochrone_polys[trip_time].append(hull)
                
    unioned_isochrones = {}
    for t, polys in isochrone_polys.items():
        if polys:
            unioned_isochrones[t] = gpd.GeoSeries(polys).unary_union
    return unioned_isochrones
