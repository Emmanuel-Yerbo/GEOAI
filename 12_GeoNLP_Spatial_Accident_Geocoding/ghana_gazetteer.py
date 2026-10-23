"""
ghana_gazetteer.py
==================
Hand-curated dictionary of ~140 known accident-prone locations in Ghana.
Includes pre-coded coordinates as a geocoding fallback and an alias map
for common abbreviations found in news headlines.
"""

import re

# ── Known Locations with Pre-coded Coordinates ────────────────────────────
# Format: "Location Name": (latitude, longitude)
# These serve as a FALLBACK when Nominatim cannot resolve a name.

KNOWN_LOCATIONS = {
    # ── GREATER ACCRA ──────────────────────────────────────────────────────
    "Lapaz": (5.6145, -0.2470),
    "Mallam Junction": (5.5790, -0.2680),
    "Tetteh Quarshie": (5.6280, -0.1750),
    "Tetteh Quarshie Interchange": (5.6280, -0.1750),
    "Kwame Nkrumah Interchange": (5.5550, -0.2130),
    "Kwame Nkrumah Circle": (5.5600, -0.2200),
    "Circle": (5.5600, -0.2200),
    "Kaneshie": (5.5650, -0.2350),
    "Madina": (5.6700, -0.1670),
    "Adenta": (5.6950, -0.1550),
    "Dome": (5.6480, -0.2280),
    "Achimota": (5.6250, -0.2350),
    "Nungua Barrier": (5.6070, -0.0730),
    "Nungua": (5.5950, -0.0750),
    "Teshie": (5.5800, -0.1000),
    "Spintex Road": (5.6350, -0.1100),
    "Spintex": (5.6350, -0.1100),
    "Tema Motorway": (5.6400, -0.1200),
    "Motorway": (5.6400, -0.1200),
    "Airport Hills": (5.6050, -0.1750),
    "Airport": (5.6050, -0.1750),
    "37 Military Hospital": (5.5870, -0.1870),
    "Graphic Road": (5.5520, -0.2180),
    "Ring Road": (5.5650, -0.2100),
    "Winneba Road": (5.5350, -0.2300),
    "George Walker Bush Highway": (5.6200, -0.2450),
    "Pokuase": (5.6800, -0.3000),
    "Pokuase Interchange": (5.6800, -0.3000),
    "Weija": (5.5600, -0.3400),
    "Kasoa": (5.5300, -0.4170),
    "Tema": (5.6700, -0.0170),
    "Ashaiman": (5.6900, -0.0330),
    "Dansoman": (5.5400, -0.2600),
    "Odorkor": (5.5800, -0.2700),
    "Abeka": (5.5900, -0.2500),
    "Darkuman": (5.5750, -0.2500),
    "Dzorwulu": (5.6050, -0.2050),
    "East Legon": (5.6350, -0.1500),
    "Osu": (5.5600, -0.1700),
    "Labadi": (5.5600, -0.1500),
    "Tesano": (5.6000, -0.2350),
    "North Kaneshie": (5.5800, -0.2400),
    "Ofankor": (5.6600, -0.2800),
    "Sowutuom": (5.6300, -0.2750),
    "Haatso": (5.6600, -0.2000),
    "Atomic Junction": (5.6450, -0.2100),
    "Legon": (5.6500, -0.1870),
    "Dawhenya": (5.8200, 0.0700),
    "Prampram Junction": (5.7800, 0.1100),
    "Shiashie": (5.6150, -0.1550),

    # ── ASHANTI ────────────────────────────────────────────────────────────
    "Abrepo Junction": (6.7200, -1.6350),
    "Suame Roundabout": (6.7100, -1.6250),
    "Suame": (6.7100, -1.6250),
    "Anloga Junction": (6.6750, -1.5700),
    "Kejetia": (6.6900, -1.6200),
    "Oforikrom": (6.6800, -1.5600),
    "Tech Junction": (6.6750, -1.5650),
    "Adum": (6.6900, -1.6150),
    "Asafo": (6.6850, -1.6000),
    "Ahodwo": (6.6600, -1.6300),
    "Sofoline": (6.6800, -1.6600),
    "Kumasi": (6.6885, -1.6244),
    "Ejisu": (6.7300, -1.4700),
    "Bekwai": (6.4600, -1.5800),
    "Konongo": (6.6200, -1.2200),
    "Mampong": (7.0650, -1.4000),
    "Ejura": (7.3800, -1.3600),
    "Asokwa Interchange": (6.6600, -1.6100),
    "Santasi Roundabout": (6.6650, -1.6350),
    "Offinso": (7.0400, -1.6100),

    # ── CENTRAL ────────────────────────────────────────────────────────────
    "Winneba Junction": (5.3500, -0.6300),
    "Winneba": (5.3500, -0.6250),
    "Mankessim": (5.2700, -1.0250),
    "Cape Coast": (5.1050, -1.2460),
    "Elmina": (5.0850, -1.3500),
    "Kasoa Tollbooth": (5.5200, -0.4200),
    "Buduburam": (5.5100, -0.4400),
    "Gomoa Okyereko": (5.3200, -0.7800),
    "Gomoa Potsin": (5.3100, -0.7500),
    "Apam Junction": (5.2800, -0.8600),
    "Dompoase": (5.0500, -1.3000),
    "Saltpond": (5.2100, -1.0700),
    "Komenda Junction": (5.0300, -1.4800),

    # ── WESTERN ────────────────────────────────────────────────────────────
    "Takoradi": (4.8980, -1.7600),
    "Sekondi": (4.9300, -1.7100),
    "Tarkwa": (5.3000, -1.9900),
    "Bogoso": (5.5400, -2.0500),
    "Inchaban": (5.0200, -1.7200),
    "Apiate": (5.5100, -1.9800),
    "Bogoso-Bawdie": (5.5200, -2.0200),

    # ── EASTERN ────────────────────────────────────────────────────────────
    "Suhum": (6.0400, -0.4500),
    "Nsawam": (5.8100, -0.3500),
    "Nkawkaw": (6.5500, -0.7700),
    "Koforidua": (6.0900, -0.2600),
    "Bunso Junction": (6.2800, -0.9600),
    "Anyinam": (6.3200, -0.9900),
    "Akim Oda": (5.9300, -0.9900),
    "Kade": (6.0800, -0.8300),
    "Kyekyewere": (6.1500, -0.4200),
    "Asuboi": (6.1000, -0.5800),
    "Apedwa": (6.1300, -0.6200),

    # ── VOLTA / OTI ────────────────────────────────────────────────────────
    "Ho": (6.6000, 0.4700),
    "Sogakope": (6.0000, 0.5900),
    "Aflao": (6.1200, 1.1900),
    "Keta": (5.9200, 0.9900),
    "Kpando": (6.9900, 0.2900),
    "Hohoe": (7.1500, 0.4700),

    # ── NORTHERN ───────────────────────────────────────────────────────────
    "Tamale": (9.4000, -0.8400),
    "Kintampo": (8.0600, -1.7300),
    "Buipe": (8.7300, -1.0500),
    "Yapei": (9.1500, -1.1600),
    "Sawla": (9.2800, -2.4200),
    "Damongo": (9.0800, -1.8200),
    "Kpong": (6.1600, 0.0700),
    "Sege": (5.9200, 0.4300),
    "Ada Junction": (5.8200, 0.5700),

    # ── UPPER EAST ─────────────────────────────────────────────────────────
    "Bolgatanga": (10.7860, -0.8510),
    "Navrongo": (10.8900, -1.0900),
    "Bawku": (11.0600, -0.2400),
    "Paga": (10.9900, -1.1000),

    # ── UPPER WEST ─────────────────────────────────────────────────────────
    "Wa": (10.0600, -2.5000),
    "Tumu": (10.8800, -1.9800),
    "Lawra": (10.6300, -2.9000),

    # ── BONO / BONO EAST / AHAFO ──────────────────────────────────────────
    "Sunyani": (7.3400, -2.3300),
    "Techiman": (7.5900, -1.9400),
    "Berekum": (7.4500, -2.5800),
    "Dormaa Ahenkro": (7.3600, -2.9600),
    "Nkoranza": (7.6200, -1.7100),

    # ── INTER-CITY CORRIDORS (dangerous stretches) ────────────────────────
    "Accra-Kumasi Highway": (6.3000, -1.0000),
    "Suhum Stretch": (6.0400, -0.4500),
    "Accra-Cape Coast Road": (5.3000, -0.7500),
    "Accra-Tema Motorway": (5.6400, -0.1200),
    "Kumasi-Tamale Road": (8.0000, -1.5000),
    "Tamale-Bolgatanga Road": (10.1000, -0.8500),
    "Cape Coast-Takoradi Highway": (5.0000, -1.5000),
    "Techiman-Kintampo Road": (7.8000, -1.8500),
}


# ── Alias Map ─────────────────────────────────────────────────────────────
# Maps abbreviations and colloquial names found in news headlines
# to their canonical form in KNOWN_LOCATIONS.

ALIASES = {
    "TQ": "Tetteh Quarshie",
    "TQ Interchange": "Tetteh Quarshie Interchange",
    "GWB Highway": "George Walker Bush Highway",
    "GWB Hwy": "George Walker Bush Highway",
    "Bush Highway": "George Walker Bush Highway",
    "N1": "Accra-Tema Motorway",
    "N1 Highway": "Accra-Tema Motorway",
    "N1 Motorway": "Accra-Tema Motorway",
    "Nkrumah Circle": "Kwame Nkrumah Circle",
    "Nkrumah Interchange": "Kwame Nkrumah Interchange",
    "KNI": "Kwame Nkrumah Interchange",
    "Atomic": "Atomic Junction",
    "37 Hospital": "37 Military Hospital",
    "the Motorway": "Accra-Tema Motorway",
    "Kasoa road": "Kasoa",
    "Mallam-Kasoa": "Kasoa",
    "Mallam-Kasoa road": "Kasoa",
    "Lapaz-Mallam": "Lapaz",
    "Tech": "Tech Junction",
    "Okyereko": "Gomoa Okyereko",
    "Potsin": "Gomoa Potsin",
}


# ── Severity Keywords ─────────────────────────────────────────────────────
SEVERITY_FATAL = [
    "fatal", "killed", "died", "dead", "death", "deaths", "fatality",
    "fatalities", "perished", "lost life", "lost lives", "lost his life",
    "lost her life", "pronounced dead", "died on the spot",
    "dead on arrival", "confirmed dead"
]

SEVERITY_INJURY = [
    "injured", "injury", "injuries", "hospitalized", "admitted",
    "critical condition", "serious condition", "rushed to hospital",
    "treated and discharged", "sustained injuries", "in critical state"
]

SEVERITY_PROPERTY = [
    "property damage", "damaged", "mangled", "wrecked", "totaled",
    "crushed", "collision", "crash"
]


# ── Vehicle Type Keywords ─────────────────────────────────────────────────
VEHICLE_TYPES = {
    "trotro": ["trotro", "tro-tro", "tro tro", "minibus"],
    "tipper_truck": ["tipper truck", "tipper", "dump truck"],
    "articulated_truck": ["articulated truck", "articulated", "cargo truck", "trailer"],
    "okada": ["okada", "motorbike", "motorcycle", "motor rider"],
    "taxi": ["taxi", "cab", "uber", "bolt ride"],
    "bus": ["coach", "VIP bus", "VVIP bus", "STC bus", "OA bus", "intercity bus", "MMT bus"],
    "voxy": ["voxy", "toyota voxy", "noah", "toyota noah"],
    "sprinter": ["sprinter", "mercedes sprinter", "benz sprinter"],
    "aboboyaa": ["aboboyaa", "motorking", "motor king", "keke", "aboboya"],
    "pragya": ["pragya", "tuk-tuk", "tuk tuk", "mahama cambine", "mahama can change"],
    "fuel_tanker": ["fuel tanker", "petrol tanker", "gas tanker", "LPG tanker", "tanker truck", "oil tanker"],
    "yutong": ["yutong", "zhongtong", "king long"],
    "private_car": ["private car", "saloon car", "sedan", "SUV"],
    "bicycle": ["bicycle", "cyclist"],
    "pedestrian": ["pedestrian", "knocked down", "run over", "hawker"],
    "ambulance": ["ambulance"],
    "police_vehicle": ["police vehicle", "police van", "police car"],
}


# ── Filter Words (locations to ignore) ────────────────────────────────────
FILTER_WORDS = {
    "Ghana", "Africa", "West Africa", "Republic of Ghana",
    "United Nations", "United States", "UK", "Nigeria",
    "World Health Organization", "WHO", "NRSA",
    "National Road Safety Authority", "MTTD",
    "Motor Traffic and Transport Department",
    "Ghana Police Service", "GPS",
}


def resolve_alias(name: str) -> str:
    """Resolve a location alias to its canonical name."""
    return ALIASES.get(name, ALIASES.get(name.strip(), name))


def get_coordinates(location_name: str):
    """
    Get pre-coded coordinates for a known location.
    Returns (lat, lon) tuple or None if not found.
    """
    canonical = resolve_alias(location_name)
    return KNOWN_LOCATIONS.get(canonical)


# Pre-compile regex patterns at module level for performance
def _compile_word_pattern(word):
    """Compile a regex pattern with word boundaries."""
    return re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)

# Pre-compile all patterns
_SEVERITY_FATAL_PATTERNS = [_compile_word_pattern(kw) for kw in SEVERITY_FATAL]
_SEVERITY_INJURY_PATTERNS = [_compile_word_pattern(kw) for kw in SEVERITY_INJURY]
_SEVERITY_PROPERTY_PATTERNS = [_compile_word_pattern(kw) for kw in SEVERITY_PROPERTY]
_VEHICLE_PATTERNS = {vtype: [_compile_word_pattern(kw) for kw in keywords] for vtype, keywords in VEHICLE_TYPES.items()}
_ALIAS_PATTERNS = {alias: _compile_word_pattern(alias) for alias in ALIASES}
_LOCATION_PATTERNS_SORTED = sorted(
    [(_compile_word_pattern(loc), loc) for loc in KNOWN_LOCATIONS],
    key=lambda x: len(x[1]),
    reverse=True
)

def classify_severity(text: str) -> str:
    if not text:
        return "unknown"
    for pattern in _SEVERITY_FATAL_PATTERNS:
        if pattern.search(text):
            return "fatal"
    for pattern in _SEVERITY_INJURY_PATTERNS:
        if pattern.search(text):
            return "injury"
    for pattern in _SEVERITY_PROPERTY_PATTERNS:
        if pattern.search(text):
            return "property_damage"
    return "unknown"


def extract_vehicle_types(text: str) -> list:
    if not text:
        return ["unknown"]
    found = []
    for vehicle_type, patterns in _VEHICLE_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                found.append(vehicle_type)
                break
    return found if found else ["unknown"]


def search_gazetteer(text: str) -> list:
    if not text:
        return []
    matches = []
    # Check aliases first
    for alias, pattern in _ALIAS_PATTERNS.items():
        if pattern.search(text):
            canonical = ALIASES[alias]
            if canonical not in matches:
                matches.append(canonical)
    # Check full location names (longest first)
    for pattern, location in _LOCATION_PATTERNS_SORTED:
        if pattern.search(text):
            canonical = resolve_alias(location)
            if canonical not in matches:
                matches.append(canonical)
    return matches


if __name__ == "__main__":
    # Quick test
    sample = """
    A fatal accident occurred at the Tetteh Quarshie Interchange on the
    George Walker Bush Highway. A Toyota Voxy collided with a tipper truck,
    killing 3 people and injuring 12 others. The injured were rushed
    to 37 Military Hospital. An aboboyaa was also involved.
    """
    print("Locations found:", search_gazetteer(sample))
    print("Severity:", classify_severity(sample))
    print("Vehicles:", extract_vehicle_types(sample))
    
    # False positive test
    false_test = "The business was busy with 37 customers aged 37. The technique requires careful analysis."
    print("\nFalse positive test (should be minimal):")
    print("  Locations:", search_gazetteer(false_test))
    print("  Vehicles:", extract_vehicle_types(false_test))
    print("  Severity:", classify_severity(false_test))
    
    for loc in search_gazetteer(sample):
        coords = get_coordinates(loc)
        if coords:
            print(f"  {loc}: {coords}")
