"""
run_pipeline.py
===============
Master runner that chains all stages of the Ghana Road Accident Map pipeline.
Usage:
    python run_pipeline.py --pages 2
    python run_pipeline.py --pages 3 --center accra
    python run_pipeline.py --google-news-only
    python run_pipeline.py --csv data/my_records.csv
"""

import argparse
import csv
import json
import os
import sys
import time

# Add project root to path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🇬🇭  GHANA ROAD ACCIDENT MAP — GEOSENTIMENT PIPELINE 🇬🇭     ║
║                                                              ║
║   Stage 1: Scrape Ghanaian news websites                     ║
║   Stage 2: Fetch from Google News RSS                        ║
║   Stage 3: Extract locations via NLP                         ║
║   Stage 3.5: Sentiment Analysis & Blame Attribution          ║
║   Stage 4: Geocode locations to GPS coordinates              ║
║   Stage 4.5: Data-Driven Blackspot & PRGI Analysis           ║
║   Stage 5: Build interactive map                             ║
║   Stage 6: Generate GeoSentiment Word Clouds                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def run_stage_1(args):
    """Stage 1: Scrape news sites."""
    print("\n" + "▓" * 60)
    print("  STAGE 1 / 6  —  NEWS SCRAPER")
    print("▓" * 60)

    from news_scraper import scrape_all_sources, save_articles

    sources = args.sources if args.sources else None
    queries = args.queries if args.queries else None

    articles = scrape_all_sources(
        sources=sources,
        queries=queries,
        max_pages=args.pages,
    )

    save_articles(articles)
    return len(articles)


def run_stage_2(args):
    """Stage 2: Google News RSS."""
    print("\n" + "▓" * 60)
    print("  STAGE 2 / 6  —  GOOGLE NEWS MONITOR")
    print("▓" * 60)

    from google_monitor import fetch_google_news, load_manual_csv, save_articles

    all_articles = []

    # Google News RSS
    rss_urls = args.rss_urls if hasattr(args, "rss_urls") and args.rss_urls else None
    all_articles.extend(fetch_google_news(custom_rss_urls=rss_urls))

    # Manual CSV import
    if args.csv:
        all_articles.extend(load_manual_csv(args.csv))

    save_articles(all_articles)
    return len(all_articles)


def run_stage_3(args):
    """Stage 3: Location extraction."""
    print("\n" + "▓" * 60)
    print("  STAGE 3 / 6  —  LOCATION EXTRACTOR (NLP)")
    print("▓" * 60)

    from location_extractor import load_spacy_model, process_articles, save_extracted

    data_dir = os.path.join(PROJECT_DIR, "data")
    input_path = os.path.join(data_dir, "articles_raw.json")

    if not os.path.exists(input_path):
        print(f"  [!] No articles found at {input_path}")
        return 0

    with open(input_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"  Loaded {len(articles)} articles")

    nlp = None
    if not args.no_spacy:
        nlp = load_spacy_model()

    records = process_articles(articles, nlp)
    save_extracted(records)
    return len(records)


def run_stage_3_5(args):
    """Stage 3.5: Sentiment & Blame Analysis."""
    print("\n" + "▓" * 60)
    print("  STAGE 3.5 / 6  —  SENTIMENT ENGINE & BLAME CLASSIFIER")
    print("▓" * 60)

    from sentiment.sentiment_engine import enrich_records
    from sentiment.blame_classifier import enrich_blame_records

    data_dir = os.path.join(PROJECT_DIR, "data")
    input_csv = os.path.join(data_dir, "accidents_extracted.csv")
    output_csv = os.path.join(data_dir, "processed", "accidents_sentiment.csv")

    if not os.path.exists(input_csv):
        print(f"  [!] Extracted records not found at {input_csv}")
        return 0

    records = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"  Loaded {len(records)} extracted records for sentiment analysis")

    # Run sentiment + blame enrichment
    enriched = enrich_records(records)
    enriched = enrich_blame_records(enriched)

    # Save to processed data folder
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    if enriched:
        fieldnames = list(enriched[0].keys())
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched)

        # Overwrite extracted CSV so geocoder and downstream modules receive enriched data
        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched)

    print(f"  ✓ Sentiment & Blame analysis complete ({len(enriched)} records)")
    print(f"  File saved: {output_csv}")
    return len(enriched)


def run_stage_4(args):
    """Stage 4: Geocoding."""
    print("\n" + "▓" * 60)
    print("  STAGE 4 / 6  —  GEOCODER")
    print("▓" * 60)

    from geocoder import geocode_locations
    geocode_locations()
    return 0


def run_stage_4_5(args):
    """Stage 4.5: Spatial Blackspot Discovery & PRGI Analysis."""
    print("\n" + "▓" * 60)
    print("  STAGE 4.5 / 6  —  SPATIAL GEOAI & PRGI ANALYSIS")
    print("▓" * 60)

    from spatial.blackspot_analysis import detect_blackspots
    from spatial.prgi_calculator import calculate_prgi
    from accident_map import load_geocoded_data

    records = load_geocoded_data()
    if not records:
        print("  [!] No geocoded records found for spatial analysis.")
        return 0

    # 1. Detect Blackspots via DBSCAN + Gi*
    spatial_res = detect_blackspots(records, eps_km=10.0, min_samples=2)

    # Save Blackspots JSON
    data_dir = os.path.join(PROJECT_DIR, "data", "processed")
    os.makedirs(data_dir, exist_ok=True)
    bs_json_path = os.path.join(data_dir, "accidents_blackspots.json")
    with open(bs_json_path, "w", encoding="utf-8") as f:
        json.dump(spatial_res, f, indent=2, ensure_ascii=False)

    # Save Blackspots CSV Summary Report
    report_dir = os.path.join(PROJECT_DIR, "output", "reports")
    os.makedirs(report_dir, exist_ok=True)
    bs_csv_path = os.path.join(report_dir, "blackspot_summary.csv")

    clusters = spatial_res.get("clusters", [])
    if clusters:
        with open(bs_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(clusters[0].keys()))
            writer.writeheader()
            writer.writerows(clusters)
        print(f"  ✓ Saved Blackspot summary report: {bs_csv_path}")

    # Save Moran's I Stats
    moran_stats = spatial_res.get("morans_i", {})
    if moran_stats:
        moran_json_path = os.path.join(report_dir, "moran_stats.json")
        with open(moran_json_path, "w", encoding="utf-8") as f:
            json.dump(moran_stats, f, indent=2)
        print(f"  ✓ Saved Moran's I spatial statistics report: {moran_json_path}")

    # 2. Calculate Perception-Reality Gap Index (PRGI)
    prgi_results = calculate_prgi(records)
    prgi_csv_path = os.path.join(report_dir, "prgi_summary.csv")
    if prgi_results:
        with open(prgi_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(prgi_results[0].keys()))
            writer.writeheader()
            writer.writerows(prgi_results)
        print(f"  ✓ Saved PRGI analysis report: {prgi_csv_path}")

    # 3. Analyze Road Network Topology G(V, E) Graph Centrality
    from spatial.network_graph import analyze_road_network_topology
    analyze_road_network_topology()

    return len(clusters)


def run_stage_5(args):
    """Stage 5: Build map."""
    print("\n" + "▓" * 60)
    print("  STAGE 5 / 6  —  MAP BUILDER")
    print("▓" * 60)

    from accident_map import load_geocoded_data, build_map

    records = load_geocoded_data()
    if records:
        output_path = build_map(records, center=args.center)
        return output_path
    return None


def run_stage_6(args):
    """Stage 6: GeoSentiment Word Clouds."""
    print("\n" + "▓" * 60)
    print("  STAGE 6 / 6  —  WORD CLOUD GENERATOR")
    print("▓" * 60)

    from utils.wordcloud_generator import generate_wordclouds_by_category
    from accident_map import load_geocoded_data

    records = load_geocoded_data()
    if not records:
        print("  [!] No geocoded records found to generate word clouds.")
        return 0

    output_dir = os.path.join(PROJECT_DIR, "output", "wordclouds")
    os.makedirs(output_dir, exist_ok=True)

    print(f"  Generating word clouds for {len(records)} records...")

    from utils.wordcloud_generator import generate_wordcloud, generate_wordclouds_by_category

    # 1. Overall Ghana Wordcloud
    all_text = " ".join([f"{r.get('title', '')} {r.get('raw_text_snippet', '')} {r.get('body_text', '')}" for r in records])
    overall_path = os.path.join(output_dir, "wc_overall_ghana.png")
    generate_wordcloud(all_text, "Ghana Road Accidents — National Context", overall_path)

    # 2. Categorized Wordclouds
    v_clouds = generate_wordclouds_by_category(records, "vehicle_types", output_dir, prefix="wc_vehicle_")
    s_clouds = generate_wordclouds_by_category(records, "severity", output_dir, prefix="wc_severity_")
    b_clouds = generate_wordclouds_by_category(records, "blame_primary", output_dir, prefix="wc_blame_")
    l_clouds = generate_wordclouds_by_category(records, "location_name", output_dir, prefix="wc_location_")

    total = 1 + len(v_clouds) + len(s_clouds) + len(b_clouds) + len(l_clouds)
    print(f"  ✓ Generated {total} word cloud visual artifacts in {output_dir}")
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Run the Ghana Accident Map pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py --pages 2
  python run_pipeline.py --pages 3 --center accra
  python run_pipeline.py --google-news-only
  python run_pipeline.py --csv data/my_records.csv
  python run_pipeline.py --news-only --sources citinewsroom myjoyonline
        """
    )

    # Data source options
    parser.add_argument("--pages", type=int, default=2,
                        help="Search result pages to scrape per query (default: 2)")
    parser.add_argument("--sources", nargs="+", default=None,
                        help="Specific news sources to scrape")
    parser.add_argument("--queries", nargs="+", default=None,
                        help="Custom search queries")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path to manual CSV file to import")
    parser.add_argument("--rss-urls", nargs="+", default=None,
                        help="Custom Google Alerts RSS URLs")

    # Mode options
    parser.add_argument("--news-only", action="store_true",
                        help="Only run news scraper (skip Google News)")
    parser.add_argument("--google-news-only", action="store_true",
                        help="Only run Google News RSS (skip direct scraping)")
    parser.add_argument("--skip-scrape", action="store_true",
                        help="Skip stages 1-2, use existing articles_raw.json")
    parser.add_argument("--skip-wordclouds", action="store_true",
                        help="Skip stage 6 word cloud generation")

    # NLP options
    parser.add_argument("--no-spacy", action="store_true",
                        help="Skip spaCy NER, use gazetteer only")

    # Map options
    parser.add_argument("--center", type=str, default="ghana",
                        choices=["ghana", "accra", "kumasi"],
                        help="Map center (default: ghana)")

    # Stage selection
    parser.add_argument("--stage", type=float, default=None,
                        choices=[1, 2, 3, 3.5, 4, 4.5, 5, 6],
                        help="Run only a specific stage")

    args = parser.parse_args()

    if args.news_only and args.google_news_only:
        parser.error("--news-only and --google-news-only cannot be used together")

    print_banner()
    start_time = time.time()

    try:
        if args.stage:
            # Run single stage
            stage_funcs = {
                1: run_stage_1, 2: run_stage_2, 3: run_stage_3,
                3.5: run_stage_3_5, 4: run_stage_4, 4.5: run_stage_4_5,
                5: run_stage_5, 6: run_stage_6
            }
            stage_funcs[args.stage](args)
        else:
            # Run full pipeline
            if not args.skip_scrape:
                if not args.google_news_only:
                    run_stage_1(args)

                if not args.news_only:
                    run_stage_2(args)

            raw_path = os.path.join(PROJECT_DIR, "data", "articles_raw.json")
            if not os.path.exists(raw_path):
                print("\n  [!] No articles found. Stages 1-2 produced no data.")
                print("      Check your internet connection or try different queries.")
                sys.exit(1)

            run_stage_3(args)
            run_stage_3_5(args)
            run_stage_4(args)
            run_stage_4_5(args)
            map_path = run_stage_5(args)

            if not args.skip_wordclouds:
                run_stage_6(args)

            elapsed = time.time() - start_time

            print(f"\n{'═'*60}")
            print(f"  ✅ GEOSENTIMENT PIPELINE COMPLETE!")
            print(f"{'═'*60}")
            print(f"  Time elapsed: {elapsed:.1f} seconds")
            if map_path:
                print(f"  Map file: {map_path}")
                print(f"\n  Open the HTML file in your browser to explore the map!")
            print(f"{'═'*60}\n")

    except KeyboardInterrupt:
        print("\n\n  [!] Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [!] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
