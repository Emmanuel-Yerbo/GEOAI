"""
geocoder.py
===========
Stage 4: Geocodes extracted location names into GPS coordinates
using OpenStreetMap Nominatim (free, no API key) with a local
cache and Ghana Gazetteer fallback.
"""

import csv
import json
import os

try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    _GEOPY_AVAILABLE = True
except ImportError:
    _GEOPY_AVAILABLE = False
    print("[!] geopy package not found. Using gazetteer pre-coded coordinates fallback.")

from ghana_gazetteer import get_coordinates, resolve_alias

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Ghana bounding box for validation
GHANA_BOUNDS = {
    "lat_min": 4.5,
    "lat_max": 11.2,
    "lon_min": -3.3,
    "lon_max": 1.2,
}


def is_in_ghana(lat: float, lon: float) -> bool:
    """Check if coordinates fall within Ghana's bounding box."""
    return (
        GHANA_BOUNDS["lat_min"] <= lat <= GHANA_BOUNDS["lat_max"]
        and GHANA_BOUNDS["lon_min"] <= lon <= GHANA_BOUNDS["lon_max"]
    )


def load_geocode_cache() -> dict:
    """Load cached geocodes to avoid duplicate API calls."""
    cache_path = os.path.join(DATA_DIR, "cache", "geocode_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_geocode_cache(cache: dict):
    """Save geocode cache atomically."""
    cache_dir = os.path.join(DATA_DIR, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "geocode_cache.json")
    tmp_path = cache_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, cache_path)


def geocode_locations(input_path: str = None, output_path: str = None):
    """Geocode extracted locations."""
    if input_path is None:
        input_path = os.path.join(DATA_DIR, "accidents_extracted.csv")
    if output_path is None:
        output_path = os.path.join(DATA_DIR, "accidents_geocoded.csv")

    if not os.path.exists(input_path):
        print(f"  [!] Input file not found: {input_path}")
        return

    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"  Loaded {len(records)} extracted records for geocoding")

    cache = load_geocode_cache()

    # Initialize Nominatim if available
    geocode_api = None
    if _GEOPY_AVAILABLE:
        try:
            geolocator = Nominatim(user_agent="ghana_accident_map_v2")
            geocode_api = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)
        except Exception as e:
            print(f"  [!] Nominatim initialization error: {e}")

    geocoded_count = 0
    cache_hits = 0
    gazetteer_hits = 0
    api_hits = 0

    geocoded_records = []

    for idx, r in enumerate(records):
        location_name = r.get("location_name", "").strip()
        if not location_name:
            continue

        canonical_name = resolve_alias(location_name)
        search_query = f"{canonical_name}, Ghana"

        lat, lon = None, None

        # 1. Check cache
        if canonical_name in cache:
            coords = cache[canonical_name]
            if coords:
                lat, lon = coords
                cache_hits += 1
        # 2. Check gazetteer fallback
        elif get_coordinates(canonical_name):
            coords = get_coordinates(canonical_name)
            lat, lon = coords
            cache[canonical_name] = [lat, lon]
            gazetteer_hits += 1
        # 3. Query Nominatim API
        elif geocode_api:
            try:
                loc = geocode_api(search_query)
                if loc and is_in_ghana(loc.latitude, loc.longitude):
                    lat, lon = loc.latitude, loc.longitude
                    cache[canonical_name] = [lat, lon]
                    api_hits += 1
                else:
                    # Negative cache (cache None so we don't query again)
                    cache[canonical_name] = None
            except Exception:
                cache[canonical_name] = None

        if lat is not None and lon is not None:
            record_copy = dict(r)
            record_copy["latitude"] = round(lat, 5)
            record_copy["longitude"] = round(lon, 5)
            geocoded_records.append(record_copy)
            geocoded_count += 1

    save_geocode_cache(cache)

    if geocoded_records:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        fieldnames = list(geocoded_records[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(geocoded_records)

    print(f"\n  ✓ Geocoding Complete: {geocoded_count} / {len(records)} records geocoded")
    print(f"    - Cache hits: {cache_hits}")
    print(f"    - Gazetteer pre-coded hits: {gazetteer_hits}")
    print(f"    - Nominatim API hits: {api_hits}")
    print(f"  File saved: {output_path}")
