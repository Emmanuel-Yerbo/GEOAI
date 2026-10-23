# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   🇬🇭 GHANA ROAD ACCIDENT MAP — NEWS MINING PIPELINE 🇬🇭     ║
║                                                              ║
║   A complete pipeline to scrape Ghanaian news sites for      ║
║   road accident reports, extract locations via NLP,          ║
║   geocode them, and build an interactive map.                ║
║                                                              ║
║   Run this notebook top-to-bottom in Google Colab.           ║
╚══════════════════════════════════════════════════════════════╝
"""

# %% [markdown]
# # 🇬🇭 Interactive Ghana Road Traffic Accident Map
#
# This notebook builds an interactive accident heatmap by:
# 1. **Scraping** Ghanaian news websites for road accident articles
# 2. **Fetching** Google News RSS feeds for wider coverage
# 3. **Extracting** location names using NLP (spaCy + custom Ghana Gazetteer)
# 4. **Geocoding** locations to GPS coordinates (Nominatim — free, no API key)
# 5. **Building** a premium interactive Folium map
#
# **No API keys required. No paid services. Everything is free.**

# %% [markdown]
# ## 📦 Stage 0: Install Dependencies

# %%
# ── INSTALL DEPENDENCIES ─────────────────────────────────────────────────
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

install("requests")
install("beautifulsoup4")
install("lxml")
install("feedparser")
install("spacy")
install("geopy")
install("folium")
install("pandas")

# Download spaCy English model
subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm", "-q"])

print("✅ All dependencies installed!")

# %% [markdown]
# ## 🗺️ Stage 1: Ghana Gazetteer
# A hand-curated dictionary of ~120 known accident-prone locations in Ghana,
# with pre-coded GPS coordinates, aliases, and keyword classifiers.

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 1: GHANA GAZETTEER
# ══════════════════════════════════════════════════════════════════════════

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

    # ── CENTRAL ────────────────────────────────────────────────────────────
    "Winneba Junction": (5.3500, -0.6300),
    "Winneba": (5.3500, -0.6250),
    "Mankessim": (5.2700, -1.0250),
    "Cape Coast": (5.1050, -1.2460),
    "Elmina": (5.0850, -1.3500),
    "Kasoa Tollbooth": (5.5200, -0.4200),
    "Buduburam": (5.5100, -0.4400),

    # ── WESTERN ────────────────────────────────────────────────────────────
    "Takoradi": (4.8980, -1.7600),
    "Sekondi": (4.9300, -1.7100),
    "Tarkwa": (5.3000, -1.9900),
    "Bogoso": (5.5400, -2.0500),
    "Inchaban": (5.0200, -1.7200),

    # ── EASTERN ────────────────────────────────────────────────────────────
    "Suhum": (6.0400, -0.4500),
    "Nsawam": (5.8100, -0.3500),
    "Nkawkaw": (6.5500, -0.7700),
    "Koforidua": (6.0900, -0.2600),
    "Bunso Junction": (6.2800, -0.9600),
    "Anyinam": (6.3200, -0.9900),
    "Akim Oda": (5.9300, -0.9900),
    "Kade": (6.0800, -0.8300),

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

    # ── INTER-CITY CORRIDORS ──────────────────────────────────────────────
    "Accra-Kumasi Highway": (6.3000, -1.0000),
    "Suhum Stretch": (6.0400, -0.4500),
    "Accra-Cape Coast Road": (5.3000, -0.7500),
    "Accra-Tema Motorway": (5.6400, -0.1200),
    "Kumasi-Tamale Road": (8.0000, -1.5000),
    "Tamale-Bolgatanga Road": (10.1000, -0.8500),
    "Cape Coast-Takoradi Highway": (5.0000, -1.5000),
    "Techiman-Kintampo Road": (7.8000, -1.8500),
}

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
    "37": "37 Military Hospital",
    "37 Hospital": "37 Military Hospital",
    "the Motorway": "Accra-Tema Motorway",
    "Kasoa road": "Kasoa",
    "Mallam-Kasoa": "Kasoa",
    "Mallam-Kasoa road": "Kasoa",
    "Lapaz-Mallam": "Lapaz",
    "Tech": "Tech Junction",
}

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

VEHICLE_TYPES = {
    "trotro": ["trotro", "tro-tro", "tro tro", "minibus"],
    "tipper_truck": ["tipper truck", "tipper", "dump truck"],
    "articulated_truck": ["articulated truck", "articulated", "cargo truck", "trailer"],
    "okada": ["okada", "motorbike", "motorcycle", "motor rider"],
    "taxi": ["taxi", "cab"],
    "bus": ["bus", "coach", "VIP bus", "VVIP bus", "STC bus", "OA bus", "intercity bus"],
    "private_car": ["private car", "saloon car", "sedan", "SUV", "vehicle"],
    "bicycle": ["bicycle", "cyclist", "bike"],
    "pedestrian": ["pedestrian", "knocked down", "run over"],
}

FILTER_WORDS = {
    "Ghana", "Africa", "West Africa", "Republic of Ghana",
    "United Nations", "United States", "UK", "Nigeria",
    "World Health Organization", "WHO", "NRSA",
    "National Road Safety Authority", "MTTD",
    "Motor Traffic and Transport Department",
    "Ghana Police Service", "GPS",
}


def resolve_alias(name):
    """Resolve a location alias to its canonical name."""
    return ALIASES.get(name, ALIASES.get(name.strip(), name))


def get_coordinates(location_name):
    """Get pre-coded coordinates for a known location. Returns (lat, lon) or None."""
    canonical = resolve_alias(location_name)
    return KNOWN_LOCATIONS.get(canonical)


def classify_severity(text):
    """Classify accident severity from article text."""
    text_lower = text.lower()
    for keyword in SEVERITY_FATAL:
        if keyword in text_lower:
            return "fatal"
    for keyword in SEVERITY_INJURY:
        if keyword in text_lower:
            return "injury"
    for keyword in SEVERITY_PROPERTY:
        if keyword in text_lower:
            return "property_damage"
    return "unknown"


def extract_vehicle_types(text):
    """Extract vehicle types mentioned in the text."""
    text_lower = text.lower()
    found = []
    for vehicle_type, keywords in VEHICLE_TYPES.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(vehicle_type)
                break
    return found if found else ["unknown"]


def search_gazetteer(text):
    """Search article text for known location names from the gazetteer."""
    text_lower = text.lower()
    matches = []

    for alias, canonical in ALIASES.items():
        if alias.lower() in text_lower:
            if canonical not in matches:
                matches.append(canonical)

    sorted_locations = sorted(KNOWN_LOCATIONS.keys(), key=len, reverse=True)
    for location in sorted_locations:
        if location.lower() in text_lower:
            canonical = resolve_alias(location)
            if canonical not in matches:
                matches.append(canonical)

    return matches


# Quick test
sample = "Fatal accident at Tetteh Quarshie Interchange involving a trotro and tipper truck. 3 killed."
print("🧪 Gazetteer Test:")
print(f"   Locations: {search_gazetteer(sample)}")
print(f"   Severity:  {classify_severity(sample)}")
print(f"   Vehicles:  {extract_vehicle_types(sample)}")
print("✅ Gazetteer loaded!")

# %% [markdown]
# ## 📰 Stage 2: News Scraper
# Scrapes 5 Ghanaian news websites for road accident articles.

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 2: NEWS SCRAPER
# ══════════════════════════════════════════════════════════════════════════

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
DELAY_SECONDS = 2

NEWS_SOURCES = {
    "citinewsroom": {
        "name": "Citinewsroom",
        "search_url": "https://citinewsroom.com/?s={query}&paged={page}",
        "article_selector": "article",
        "title_selector": "h2 a, h3 a, .entry-title a",
        "link_selector": "h2 a, h3 a, .entry-title a",
        "date_selector": "time, .entry-date, .post-date",
        "body_selectors": [".entry-content", ".post-content", "article p"],
    },
    "myjoyonline": {
        "name": "MyJoyOnline",
        "search_url": "https://www.myjoyonline.com/?s={query}&paged={page}",
        "article_selector": "article, .post-item, .search-result",
        "title_selector": "h2 a, h3 a, .entry-title a",
        "link_selector": "h2 a, h3 a, .entry-title a",
        "date_selector": "time, .entry-date, .post-date, .date",
        "body_selectors": [".entry-content", ".post-content", ".article-content", "article p"],
    },
    "graphic": {
        "name": "Graphic Online",
        "search_url": "https://www.graphic.com.gh/?s={query}&paged={page}",
        "article_selector": "article, .post-item",
        "title_selector": "h2 a, h3 a, .entry-title a",
        "link_selector": "h2 a, h3 a, .entry-title a",
        "date_selector": "time, .entry-date, .post-date",
        "body_selectors": [".entry-content", ".post-content", "article p"],
    },
    "ghanaweb": {
        "name": "GhanaWeb",
        "search_url": "https://www.ghanaweb.com/GhanaHomePage/search.php?query={query}&page={page}",
        "article_selector": ".search-result, .story-link, article",
        "title_selector": "a, h2 a, h3 a",
        "link_selector": "a",
        "date_selector": ".date, time, span.date",
        "body_selectors": [".article-text", ".story-body", "#article-body", "article p"],
    },
    "modernghana": {
        "name": "ModernGhana",
        "search_url": "https://www.modernghana.com/search?q={query}&page={page}",
        "article_selector": ".news-item, article, .search-result",
        "title_selector": "a, h2 a, h3 a",
        "link_selector": "a",
        "date_selector": ".date, time, .news-date",
        "body_selectors": [".article-body", ".news-content", "#article-content", "article p"],
    },
}

SEARCH_QUERIES = [
    "road accident",
    "road crash",
    "fatal accident",
]


def fetch_page(url):
    """Fetch a page and return parsed BeautifulSoup object."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"  [!] Failed to fetch {url}: {e}")
        return None


def extract_article_links(soup, source_config):
    """Extract article URLs and titles from a search results page."""
    articles = []
    containers = soup.select(source_config["article_selector"])

    for container in containers:
        link_tag = container.select_one(source_config["link_selector"])
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        title = link_tag.get_text(strip=True)
        if not href or not title:
            continue

        date_tag = container.select_one(source_config["date_selector"])
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        datetime_attr = date_tag.get("datetime", "") if date_tag else ""

        articles.append({
            "title": title,
            "url": href,
            "date": datetime_attr or date_str,
        })

    return articles


def fetch_article_body(url, body_selectors):
    """Fetch the full text of an article."""
    soup = fetch_page(url)
    if not soup:
        return ""

    for selector in body_selectors:
        elements = soup.select(selector)
        if elements:
            paragraphs = []
            for el in elements:
                text = el.get_text(separator=" ", strip=True)
                if len(text) > 30:
                    paragraphs.append(text)
            if paragraphs:
                return " ".join(paragraphs)

    p_tags = soup.find_all("p")
    body = " ".join(p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 30)
    return body


def is_relevant(title, body):
    """Check if an article is actually about a road accident."""
    combined = (title + " " + body).lower()
    accident_keywords = [
        "accident", "crash", "collision", "killed", "fatal",
        "knocked", "road", "highway", "motorway", "vehicle",
        "truck", "trotro", "bus", "pedestrian", "injured"
    ]
    return sum(1 for kw in accident_keywords if kw in combined) >= 2


def scrape_news(sources=None, queries=None, max_pages=2):
    """
    Scrape Ghanaian news sources for road accident articles.

    Args:
        sources: List of source keys. None = all sources.
        queries: List of search queries. None = defaults.
        max_pages: Pages per query per source.

    Returns:
        List of article dicts.
    """
    if sources is None:
        sources = list(NEWS_SOURCES.keys())
    if queries is None:
        queries = SEARCH_QUERIES

    all_articles = []
    seen_urls = set()

    for source_key in sources:
        if source_key not in NEWS_SOURCES:
            continue
        config = NEWS_SOURCES[source_key]

        for query in queries:
            print(f"\n📰 Scraping {config['name']} — query: '{query}'")

            for page in range(1, max_pages + 1):
                url = config["search_url"].format(
                    query=query.replace(" ", "+"),
                    page=page
                )
                print(f"   [Page {page}] {url}")

                soup = fetch_page(url)
                if not soup:
                    continue

                article_links = extract_article_links(soup, config)
                print(f"   [Page {page}] Found {len(article_links)} article links")

                for article_info in article_links:
                    if article_info["url"] in seen_urls:
                        continue
                    seen_urls.add(article_info["url"])

                    time.sleep(DELAY_SECONDS)
                    body = fetch_article_body(article_info["url"], config["body_selectors"])

                    if body and is_relevant(article_info["title"], body):
                        all_articles.append({
                            "title": article_info["title"],
                            "url": article_info["url"],
                            "date": article_info["date"],
                            "body": body[:3000],
                            "source": config["name"],
                            "source_type": "news_scraper",
                            "scraped_at": datetime.now().isoformat(),
                        })
                        print(f"   ✓ {article_info['title'][:60]}...")

                time.sleep(DELAY_SECONDS)

    print(f"\n✅ News Scraping Complete: {len(all_articles)} relevant articles found")
    return all_articles

# %% [markdown]
# ## 🌐 Stage 3: Google News RSS Monitor
# Fetches accident articles from Google News RSS (free, no API key).

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 3: GOOGLE NEWS RSS MONITOR
# ══════════════════════════════════════════════════════════════════════════

import feedparser

GOOGLE_NEWS_QUERIES = [
    '"road accident" Ghana',
    '"road crash" Ghana',
    '"fatal accident" Accra',
    '"fatal accident" Kumasi',
    '"trotro accident"',
    '"truck accident" Ghana',
    '"pedestrian knocked" Ghana',
    '"accident killed" Ghana highway',
    '"road accident" Kasoa',
    '"road accident" Tamale',
]


def build_google_news_url(query):
    """Build a Google News RSS URL."""
    encoded = query.replace(" ", "+").replace('"', "%22")
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-GH&gl=GH&ceid=GH:en"


def fetch_google_news(queries=None):
    """Fetch articles from Google News RSS feeds."""
    if queries is None:
        queries = GOOGLE_NEWS_QUERIES

    articles = []
    seen_urls = set()

    print("\n🌐 Fetching Google News RSS feeds...")

    for i, query in enumerate(queries):
        rss_url = build_google_news_url(query)
        print(f"   [{i+1}/{len(queries)}] {query}")

        try:
            feed = feedparser.parse(rss_url)
            if feed.bozo and not feed.entries:
                continue

            for entry in feed.entries:
                link = entry.get("link", "")
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                published = entry.get("published", "")
                try:
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6]).isoformat()
                except (TypeError, ValueError):
                    pass

                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()

                if "<" in summary:
                    summary = BeautifulSoup(summary, "html.parser").get_text(
                        separator=" ", strip=True
                    )

                articles.append({
                    "title": title,
                    "url": link,
                    "date": published,
                    "body": summary,
                    "source": "Google News",
                    "source_type": "google_news",
                    "scraped_at": datetime.now().isoformat(),
                })

            print(f"       → {len(feed.entries)} entries found")

        except Exception as e:
            print(f"       [!] Error: {e}")

    print(f"\n✅ Google News Complete: {len(articles)} unique articles")
    return articles

# %% [markdown]
# ## 🔍 Stage 4: Location Extraction (NLP)
# Two-layer extraction: spaCy NER + Ghana Gazetteer pattern matching.

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 4: LOCATION EXTRACTION (NLP)
# ══════════════════════════════════════════════════════════════════════════

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy model loaded: en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    print("⚠️ spaCy model not found — using gazetteer-only mode")
    nlp = None
    SPACY_AVAILABLE = False


def extract_locations_spacy(text, nlp_model):
    """Extract locations using spaCy NER."""
    if nlp_model is None:
        return []
    doc = nlp_model(text[:5000])
    locations = []
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "FAC"):
            name = ent.text.strip()
            if name not in FILTER_WORDS and len(name) > 2:
                locations.append(name)
    return list(set(locations))


def extract_locations_combined(text, nlp_model=None):
    """Two-layer location extraction: spaCy + Gazetteer."""
    locations = []

    if nlp_model:
        spacy_locs = extract_locations_spacy(text, nlp_model)
        locations.extend(spacy_locs)

    gazetteer_locs = search_gazetteer(text)
    locations.extend(gazetteer_locs)

    seen = set()
    unique = []
    for loc in locations:
        canonical = resolve_alias(loc)
        if canonical not in seen:
            seen.add(canonical)
            unique.append(canonical)
    return unique


def extract_date_from_article(article):
    """Extract and normalize date from an article."""
    date_str = article.get("date", "") or article.get("scraped_at", "")
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d",
                "%B %d, %Y", "%d %B %Y", "%d/%m/%Y", "%m/%d/%Y"]:
        try:
            return datetime.strptime(date_str[:19], fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    return date_str[:10] if date_str else "unknown"


def process_articles(articles, nlp_model=None):
    """Process all articles to extract locations, severity, and vehicles."""
    records = []
    print(f"\n🔍 Processing {len(articles)} articles for locations...")

    for i, article in enumerate(articles):
        title = article.get("title", "")
        body = article.get("body", "")
        combined_text = f"{title}. {body}"

        locations = extract_locations_combined(combined_text, nlp_model)

        manual_loc = article.get("manual_location", "")
        if not locations and manual_loc:
            locations = [manual_loc]
        if not locations:
            continue

        severity = classify_severity(combined_text)
        vehicles = extract_vehicle_types(combined_text)
        date = extract_date_from_article(article)

        for loc in locations:
            records.append({
                "date": date,
                "source_type": article.get("source_type", "unknown"),
                "source": article.get("source", ""),
                "source_url": article.get("url", ""),
                "location_name": loc,
                "severity": severity,
                "vehicle_types": ", ".join(vehicles),
                "title": title[:150],
                "raw_text_snippet": combined_text[:300],
            })

        if (i + 1) % 20 == 0:
            print(f"   Processed {i+1}/{len(articles)} articles → {len(records)} location records")

    # Print summary
    from collections import Counter
    loc_counts = Counter(r["location_name"] for r in records)
    sev_counts = Counter(r["severity"] for r in records)

    print(f"\n✅ Extraction Complete: {len(records)} accident-location records")
    print(f"\n   📍 Top 10 Locations:")
    for loc, count in loc_counts.most_common(10):
        print(f"      {count:3d}x  {loc}")
    print(f"\n   💥 Severity Breakdown:")
    for sev, count in sev_counts.most_common():
        print(f"      {count:3d}x  {sev}")

    return records

# %% [markdown]
# ## 📌 Stage 5: Geocoding
# Converts location names to GPS coordinates using Nominatim (free) + Gazetteer fallback.

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 5: GEOCODING
# ══════════════════════════════════════════════════════════════════════════

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

GHANA_BOUNDS = {"lat_min": 4.5, "lat_max": 11.2, "lon_min": -3.3, "lon_max": 1.2}


def is_in_ghana(lat, lon):
    """Check if coordinates fall within Ghana's bounding box."""
    return (GHANA_BOUNDS["lat_min"] <= lat <= GHANA_BOUNDS["lat_max"]
            and GHANA_BOUNDS["lon_min"] <= lon <= GHANA_BOUNDS["lon_max"])


def geocode_records(records):
    """
    Geocode all location names in the extracted records.
    Priority: Gazetteer → Nominatim API → Skip.
    """
    geolocator = Nominatim(user_agent="ghana_accident_map_research_v1")
    geocode_func = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

    unique_locations = set(r["location_name"] for r in records)
    print(f"\n📌 Geocoding {len(unique_locations)} unique locations...")

    geocoded = {}
    cache = {}
    stats = {"gazetteer": 0, "nominatim": 0, "failed": 0}

    for i, loc_name in enumerate(sorted(unique_locations)):
        canonical = resolve_alias(loc_name)

        # Priority 1: Gazetteer
        coords = get_coordinates(canonical)
        if coords:
            geocoded[loc_name] = {"lat": coords[0], "lon": coords[1], "confidence": "gazetteer"}
            stats["gazetteer"] += 1
            print(f"   [{i+1}/{len(unique_locations)}] {canonical} → Gazetteer ✓")
            continue

        # Priority 2: Nominatim
        query = f"{canonical}, Ghana"
        print(f"   [{i+1}/{len(unique_locations)}] {canonical} → Nominatim...", end=" ")
        try:
            location = geocode_func(query)
            if location and is_in_ghana(location.latitude, location.longitude):
                geocoded[loc_name] = {
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "confidence": "nominatim"
                }
                stats["nominatim"] += 1
                print(f"✓ ({location.latitude:.4f}, {location.longitude:.4f})")
            else:
                stats["failed"] += 1
                print("✗ Not found / outside Ghana")
        except Exception as e:
            stats["failed"] += 1
            print(f"✗ Error: {e}")

    # Merge coordinates into records
    geocoded_records = []
    for record in records:
        geo = geocoded.get(record["location_name"])
        if geo:
            record["latitude"] = geo["lat"]
            record["longitude"] = geo["lon"]
            record["geocode_confidence"] = geo["confidence"]
            geocoded_records.append(record)

    print(f"\n✅ Geocoding Complete:")
    print(f"   Gazetteer hits: {stats['gazetteer']}")
    print(f"   Nominatim hits: {stats['nominatim']}")
    print(f"   Failed:         {stats['failed']}")
    print(f"   Records with coordinates: {len(geocoded_records)}")

    return geocoded_records

# %% [markdown]
# ## 🗺️ Stage 6: Build Interactive Map
# Premium dark-mode Folium map with HeatMap, MarkerCluster, and styled popups.

# %%
# ══════════════════════════════════════════════════════════════════════════
# STAGE 6: INTERACTIVE MAP BUILDER
# ══════════════════════════════════════════════════════════════════════════

import folium
from folium import plugins
from collections import Counter

GHANA_CENTER = [7.9465, -1.0232]
ACCRA_CENTER = [5.6037, -0.1870]
KUMASI_CENTER = [6.6885, -1.6244]

SEVERITY_COLORS = {
    "fatal": "red",
    "injury": "orange",
    "property_damage": "yellow",
    "unknown": "blue",
}


def create_popup_html(record):
    """Create a styled HTML popup card."""
    severity = record.get("severity", "unknown")
    sev_color_map = {"fatal": "#e74c3c", "injury": "#e67e22",
                     "property_damage": "#f1c40f", "unknown": "#3498db"}
    sev_color = sev_color_map.get(severity, "#3498db")

    return f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;width:280px;border-radius:8px;
                overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.3);">
        <div style="background:{sev_color};color:white;padding:8px 12px;font-size:11px;
                    font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
            {severity.replace('_', ' ')} ACCIDENT
        </div>
        <div style="padding:10px 12px;background:#1a1a2e;color:#e0e0e0;">
            <div style="font-size:13px;font-weight:600;margin-bottom:6px;color:#fff;">
                📍 {record.get('location_name', 'Unknown')}
            </div>
            <div style="font-size:11px;color:#aaa;margin-bottom:6px;">
                📅 {record.get('date', 'Unknown')}
            </div>
            <div style="font-size:11px;margin-bottom:8px;line-height:1.4;color:#ccc;">
                {record.get('title', '')[:120]}
            </div>
            <div style="font-size:10px;color:#888;margin-bottom:6px;">
                🚗 {record.get('vehicle_types', 'unknown')} | 📰 {record.get('source', '')}
            </div>
            <a href="{record.get('source_url', '#')}" target="_blank"
               style="display:inline-block;font-size:10px;color:#64ffda;text-decoration:none;
                      border:1px solid #64ffda;padding:3px 8px;border-radius:4px;">
                🔗 Read Full Article
            </a>
        </div>
    </div>
    """


def build_accident_map(records, center="ghana"):
    """Build the premium interactive accident map."""
    if not records:
        print("  [!] No records to map. Check previous stages.")
        return None

    centers = {"ghana": (GHANA_CENTER, 7), "accra": (ACCRA_CENTER, 12), "kumasi": (KUMASI_CENTER, 12)}
    map_center, zoom = centers.get(center, (GHANA_CENTER, 7))

    # ── Base Map ──────────────────────────────────────────────────────────
    m = folium.Map(location=map_center, zoom_start=zoom, tiles=None, control_scale=True)

    folium.TileLayer(tiles="CartoDB dark_matter", name="🌙 Dark Mode").add_to(m)
    folium.TileLayer(tiles="CartoDB positron", name="☀️ Light Mode").add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="🗺️ Street Map").add_to(m)

    # ── HeatMap Layer ─────────────────────────────────────────────────────
    heat_data = []
    for r in records:
        weight = {"fatal": 3, "injury": 2, "property_damage": 1, "unknown": 1}
        w = weight.get(r.get("severity", "unknown"), 1)
        heat_data.append([r["latitude"], r["longitude"], w])

    plugins.HeatMap(
        heat_data, name="🔥 Heat Map", min_opacity=0.3, max_zoom=15,
        radius=20, blur=15,
        gradient={0.2: "#00ff00", 0.4: "#adff2f", 0.6: "#ffff00", 0.8: "#ff8c00", 1.0: "#ff0000"},
    ).add_to(m)

    # ── MarkerCluster Layer ───────────────────────────────────────────────
    marker_cluster = plugins.MarkerCluster(name="📍 Individual Accidents", show=False)
    for r in records:
        severity = r.get("severity", "unknown")
        color = SEVERITY_COLORS.get(severity, "blue")
        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup=folium.Popup(create_popup_html(r), max_width=300),
            tooltip=f"{r.get('location_name', 'Unknown')} — {severity}",
            icon=folium.Icon(color=color, icon="info-sign", prefix="glyphicon"),
        ).add_to(marker_cluster)
    marker_cluster.add_to(m)

    # ── Severity Layers ───────────────────────────────────────────────────
    for sev_name, sev_color in SEVERITY_COLORS.items():
        sev_records = [r for r in records if r.get("severity") == sev_name]
        if not sev_records:
            continue
        emoji = {"fatal": "💀", "injury": "🩹", "property_damage": "🚗", "unknown": "❓"}
        layer_name = f"{emoji.get(sev_name, '')} {sev_name.replace('_',' ').title()} ({len(sev_records)})"
        sev_group = folium.FeatureGroup(name=layer_name, show=False)
        for r in sev_records:
            folium.CircleMarker(
                location=[r["latitude"], r["longitude"]], radius=8,
                color=sev_color, fill=True, fill_color=sev_color, fill_opacity=0.7,
                popup=folium.Popup(create_popup_html(r), max_width=300),
                tooltip=r.get("location_name", ""),
            ).add_to(sev_group)
        sev_group.add_to(m)

    # ── Controls ──────────────────────────────────────────────────────────
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(tile_layer="CartoDB dark_matter", position="bottomright",
                    width=120, height=120).add_to(m)

    # ── Title Overlay ─────────────────────────────────────────────────────
    loc_counts = Counter(r["location_name"] for r in records)
    top_loc = loc_counts.most_common(1)[0] if loc_counts else ("N/A", 0)

    title_html = f"""
    <div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;
                background:rgba(10,10,30,0.85);backdrop-filter:blur(10px);color:white;
                padding:12px 24px;border-radius:12px;font-family:'Segoe UI',Arial,sans-serif;
                box-shadow:0 4px 20px rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.1);
                text-align:center;">
        <div style="font-size:16px;font-weight:700;letter-spacing:1px;">
            🇬🇭 GHANA ROAD ACCIDENT MAP
        </div>
        <div style="font-size:11px;color:#aaa;margin-top:4px;">
            {len(records)} incidents mapped | Most dangerous:
            <span style="color:#ff4444;font-weight:600;">{top_loc[0]}</span> ({top_loc[1]} reports)
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # ── Legend ────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed;bottom:30px;left:10px;z-index:9999;
                background:rgba(10,10,30,0.85);backdrop-filter:blur(10px);color:white;
                padding:10px 14px;border-radius:8px;font-family:'Segoe UI',Arial,sans-serif;
                font-size:11px;box-shadow:0 2px 10px rgba(0,0,0,0.4);
                border:1px solid rgba(255,255,255,0.1);">
        <div style="font-weight:700;margin-bottom:6px;">SEVERITY</div>
        <div>🔴 Fatal</div><div>🟠 Injury</div><div>🟡 Property Damage</div><div>🔵 Unknown</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    print(f"\n✅ Map built with {len(records)} incidents!")
    return m

# %% [markdown]
# ## 🚀 Stage 7: RUN THE FULL PIPELINE
# Execute all stages in sequence. Adjust the parameters below.

# %%
# ══════════════════════════════════════════════════════════════════════════
# 🚀 RUN THE FULL PIPELINE
# ══════════════════════════════════════════════════════════════════════════

# ┌──────────────────────────────────────────────────────────────────┐
# │  ⚙️ CONFIGURATION — Adjust these values before running          │
# └──────────────────────────────────────────────────────────────────┘

# Which news sources to scrape (comment out any you don't want)
SOURCES_TO_SCRAPE = [
    "citinewsroom",
    "myjoyonline",
    # "graphic",       # Uncomment to include
    # "ghanaweb",      # Uncomment to include
    # "modernghana",   # Uncomment to include
]

# Number of search result pages to scrape per query per source
PAGES_TO_SCRAPE = 2  # Start small, increase later

# Map center: "ghana" (country-wide), "accra", or "kumasi"
MAP_CENTER = "ghana"

# Set to True to also fetch Google News RSS feeds
USE_GOOGLE_NEWS = True

# ┌──────────────────────────────────────────────────────────────────┐
# │  🏃 EXECUTION — Run this cell to start the pipeline             │
# └──────────────────────────────────────────────────────────────────┘

import time
start_time = time.time()

print("╔══════════════════════════════════════════════════════════════╗")
print("║   🇬🇭  RUNNING GHANA ACCIDENT MAP PIPELINE                  ║")
print("╚══════════════════════════════════════════════════════════════╝")

# Stage 1: Scrape news
all_articles = []
print("\n" + "▓" * 60)
print("  STAGE 1/5 — NEWS SCRAPER")
print("▓" * 60)
news_articles = scrape_news(sources=SOURCES_TO_SCRAPE, max_pages=PAGES_TO_SCRAPE)
all_articles.extend(news_articles)

# Stage 2: Google News RSS
if USE_GOOGLE_NEWS:
    print("\n" + "▓" * 60)
    print("  STAGE 2/5 — GOOGLE NEWS RSS")
    print("▓" * 60)
    google_articles = fetch_google_news()
    all_articles.extend(google_articles)

print(f"\n📊 Total articles collected: {len(all_articles)}")

# Stage 3: Extract locations
print("\n" + "▓" * 60)
print("  STAGE 3/5 — LOCATION EXTRACTION (NLP)")
print("▓" * 60)
extracted_records = process_articles(all_articles, nlp)

# Stage 4: Geocode
print("\n" + "▓" * 60)
print("  STAGE 4/5 — GEOCODING")
print("▓" * 60)
geocoded_records = geocode_records(extracted_records)

# Stage 5: Build Map
print("\n" + "▓" * 60)
print("  STAGE 5/5 — BUILDING MAP")
print("▓" * 60)
accident_map = build_accident_map(geocoded_records, center=MAP_CENTER)

elapsed = time.time() - start_time
print(f"\n{'═'*60}")
print(f"  ✅ PIPELINE COMPLETE!")
print(f"  ⏱️  Time: {elapsed:.1f} seconds")
print(f"  📊 Articles scraped: {len(all_articles)}")
print(f"  📍 Location records: {len(extracted_records)}")
print(f"  🗺️  Mapped incidents: {len(geocoded_records)}")
print(f"{'═'*60}")

# %% [markdown]
# ## 🗺️ Display the Map
# Run this cell to display the interactive map directly in Colab.

# %%
# ── Display the map in Colab ──────────────────────────────────────────────
if accident_map is not None:
    # Display inline in Colab
    try:
        display(accident_map)
    except NameError:
        print("Map saved. Open the HTML file to view.")

    # Also save as HTML (downloadable from Colab Files panel)
    accident_map.save("ghana_accident_map.html")
    print("💾 Map saved as 'ghana_accident_map.html'")
    print("   → Download from the Files panel on the left sidebar")
else:
    print("⚠️ No map generated — check if articles were found in previous stages.")

# %% [markdown]
# ## 📊 Bonus: Data Summary Table
# View the geocoded data as a pandas DataFrame.

# %%
# ── Data Summary ──────────────────────────────────────────────────────────
import pandas as pd

if geocoded_records:
    df = pd.DataFrame(geocoded_records)
    print(f"📊 Dataset: {len(df)} rows × {len(df.columns)} columns\n")

    # Top dangerous locations
    print("🔴 TOP 15 MOST DANGEROUS LOCATIONS:")
    print(df["location_name"].value_counts().head(15).to_string())

    print(f"\n💥 SEVERITY BREAKDOWN:")
    print(df["severity"].value_counts().to_string())

    print(f"\n🚗 VEHICLE TYPES INVOLVED:")
    print(df["vehicle_types"].value_counts().head(10).to_string())

    # Display table
    try:
        display(df[["date", "location_name", "severity", "vehicle_types", "source", "latitude", "longitude"]].head(20))
    except NameError:
        print("Map saved. Open the HTML file to view.")

    # Save to CSV (downloadable)
    df.to_csv("ghana_accidents_data.csv", index=False)
    print("\n💾 Data saved as 'ghana_accidents_data.csv'")
else:
    print("⚠️ No geocoded data available.")
