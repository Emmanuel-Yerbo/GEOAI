"""
location_extractor.py
=====================
Stage 3: Extracts location names from scraped article text using
a two-layer approach: spaCy NER + custom Ghana Gazetteer.
"""

import json
import os
import csv
import sys
from datetime import datetime
from collections import Counter

# Try to import spaCy — fall back to gazetteer-only mode if not installed
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("[!] spaCy not installed. Using gazetteer-only mode.")
    print("    Install with: pip install spacy && python -m spacy download en_core_web_sm")

from ghana_gazetteer import (
    search_gazetteer, classify_severity, extract_vehicle_types,
    FILTER_WORDS, resolve_alias
)

FILTER_WORDS_LOWER = {w.lower() for w in FILTER_WORDS}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_spacy_model():
    """Load spaCy English model."""
    if not SPACY_AVAILABLE:
        return None
    try:
        nlp = spacy.load("en_core_web_sm")
        print("  ✓ spaCy model loaded: en_core_web_sm")
        return nlp
    except OSError:
        print("  [!] spaCy model not found. Install with:")
        print("      python -m spacy download en_core_web_sm")
        return None


def extract_locations_spacy(text: str, nlp) -> list:
    """
    Extract location names from text using spaCy NER.
    Returns list of location name strings.
    """
    if nlp is None:
        return []

    doc = nlp(text[:5000])  # Limit text length for performance
    locations = []

    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "FAC"):
            name = ent.text.strip()
            # Filter out country-level and irrelevant entities
            if name.lower() not in FILTER_WORDS_LOWER and len(name) > 2:
                locations.append(name)

    return list(set(locations))


def extract_locations_combined(text: str, nlp=None) -> list:
    """
    Two-layer location extraction:
    1. spaCy NER (catches general locations)
    2. Ghana Gazetteer (catches local names spaCy misses)

    Returns deduplicated list of location names.
    """
    locations = []

    # Layer 1: spaCy NER
    if nlp:
        spacy_locs = extract_locations_spacy(text, nlp)
        locations.extend(spacy_locs)

    # Layer 2: Gazetteer pattern matching
    gazetteer_locs = search_gazetteer(text)
    locations.extend(gazetteer_locs)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for loc in locations:
        canonical = resolve_alias(loc)
        if canonical not in seen:
            seen.add(canonical)
            unique.append(canonical)

    return unique


def extract_date(article: dict) -> str:
    date_str = article.get("date", "")
    if not date_str:
        date_str = article.get("scraped_at", "")
    if not date_str:
        return "unknown"
    # Try dateutil first (handles most formats)
    try:
        from dateutil import parser as dateutil_parser
        dt = dateutil_parser.parse(date_str, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError, ImportError):
        pass
    # Fallback: manual formats
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(date_str.strip()[:19], fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    return date_str[:10] if date_str else "unknown"


def process_articles(articles: list, nlp=None) -> list:
    """
    Process all articles to extract locations, severity, and vehicle types.

    Returns list of accident records (one per location per article).
    """
    records = []

    print(f"\n  Processing {len(articles)} articles...")

    for i, article in enumerate(articles):
        title = article.get("title") or ""
        body = article.get("body") or ""
        combined_text = f"{title}. {body}"

        # Extract locations
        locations = extract_locations_combined(combined_text, nlp)

        if not locations:
            # Check if manual_location was provided (from CSV import)
            manual_loc = article.get("manual_location", "")
            if manual_loc:
                locations = [manual_loc]
            else:
                continue  # Skip if no location found

        # Extract metadata
        severity = classify_severity(combined_text)
        vehicles = extract_vehicle_types(combined_text)
        date = extract_date(article)

        # Create one record per location
        for loc in locations:
            records.append({
                "date": date,
                "source_type": article.get("source_type", "unknown"),
                "source": article.get("source", ""),
                "source_url": article.get("url", ""),
                "location_name": loc,
                "severity": severity,
                "vehicle_types": ", ".join(vehicles),
                "title": (title or "")[:150],
                "raw_text_snippet": combined_text[:300],
            })

        if (i + 1) % 10 == 0:
            print(f"    Processed {i+1}/{len(articles)} articles, {len(records)} location records found")

    print(f"\n  ✓ Extraction complete: {len(records)} accident-location records from {len(articles)} articles")
    return records


def save_extracted(records: list, filepath: str = None):
    """Save extracted records to CSV."""
    if filepath is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, "accidents_extracted.csv")

    if not records:
        print("  [!] No records to save.")
        return

    fieldnames = [
        "date", "source_type", "source", "source_url",
        "location_name", "severity", "vehicle_types",
        "title", "raw_text_snippet"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\n{'='*60}")
    print(f"  SAVED: {len(records)} records")
    print(f"  File: {filepath}")
    print(f"{'='*60}")

    # Print summary statistics
    loc_counts = Counter(r["location_name"] for r in records)
    sev_counts = Counter(r["severity"] for r in records)

    print(f"\n  Top 10 Locations:")
    for loc, count in loc_counts.most_common(10):
        print(f"    {count:3d}x  {loc}")

    print(f"\n  Severity Breakdown:")
    for sev, count in sev_counts.most_common():
        print(f"    {count:3d}x  {sev}")


# ── Main Entry Point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract locations from scraped accident articles."
    )
    parser.add_argument("--input", type=str, default=None,
                        help="Input JSON file (default: data/articles_raw.json)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV file (default: data/accidents_extracted.csv)")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Skip spaCy NER, use gazetteer only")

    args = parser.parse_args()

    print("\n" + "█" * 60)
    print("  LOCATION EXTRACTOR (NLP)")
    print("  Stage 3 of the Accident Map Pipeline")
    print("█" * 60)

    # Load articles
    input_path = args.input or os.path.join(DATA_DIR, "articles_raw.json")
    if not os.path.exists(input_path):
        print(f"\n  [!] Input file not found: {input_path}")
        print(f"      Run news_scraper.py or google_monitor.py first.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"\n  Loaded {len(articles)} articles from {input_path}")

    # Load spaCy model
    nlp = None
    if not args.no_spacy:
        nlp = load_spacy_model()

    # Process
    records = process_articles(articles, nlp)

    # Save
    save_extracted(records, args.output)
