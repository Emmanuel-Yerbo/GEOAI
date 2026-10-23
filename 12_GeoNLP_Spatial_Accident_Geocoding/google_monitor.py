"""
google_monitor.py
=================
Stage 2: Fetches road accident articles from Google News RSS feeds.
No API key required. No account needed. Just works.
"""

import csv
import json
import os
import time
import uuid
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote_plus

try:
    import feedparser
    _FEEDPARSER_AVAILABLE = True
except ImportError:
    _FEEDPARSER_AVAILABLE = False
    print("[!] feedparser package not found. Run 'pip install feedparser' or 'pip install -r requirements.txt'")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ── Google News RSS Queries ───────────────────────────────────────────────
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
    '"road accident" Takoradi',
    '"crash" "injured" Ghana road',
]


def build_google_news_url(query: str) -> str:
    """Build Google News RSS URL for a given query."""
    encoded_query = quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-GH&gl=GH&ceid=GH:en"


def clean_html_summary(html_content: str) -> str:
    """Clean Google News RSS summary HTML to extract plain text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(strip=True)


def parse_rss_feed(feed_url: str, query_label: str = "google_news") -> list:
    """Parse a single RSS feed and return structured article dicts."""
    if not _FEEDPARSER_AVAILABLE:
        print("  [!] feedparser unavailable. Skipping RSS feed parsing.")
        return []

    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            published = entry.get("published", entry.get("updated", ""))
            summary_raw = entry.get("summary", "")
            snippet = clean_html_summary(summary_raw)

            # Extract source domain if available
            source_info = entry.get("source", {})
            source_name = source_info.get("title", "Google News") if isinstance(source_info, dict) else "Google News"

            article = {
                "url": link,
                "title": title,
                "date_published": published,
                "body_text": snippet,
                "raw_html": summary_raw,
                "source": source_name,
                "query": query_label,
                "scraped_at": datetime.now().isoformat(),
            }
            articles.append(article)
    except Exception as e:
        print(f"  [!] RSS fetch error ({query_label}): {e}")

    return articles


def fetch_google_news(custom_rss_urls: list = None) -> list:
    """
    Fetch articles for all default Google News queries or custom RSS URLs.
    """
    if not _FEEDPARSER_AVAILABLE:
        print("\n  [!] feedparser is not installed.")
        print("      To enable Google News RSS monitoring, run: pip install feedparser")
        print("      Continuing with existing raw articles...\n")
        return []

    print("\n" + "=" * 60)
    print("  GOOGLE NEWS RSS MONITOR")
    print("=" * 60)

    all_articles = []
    seen_urls = set()

    if custom_rss_urls:
        urls_to_fetch = [(url, f"custom_rss_{i+1}") for i, url in enumerate(custom_rss_urls)]
    else:
        urls_to_fetch = [(build_google_news_url(q), q) for q in GOOGLE_NEWS_QUERIES]

    for feed_url, query_label in urls_to_fetch:
        print(f"  Fetching RSS feed for: {query_label}...")
        articles = parse_rss_feed(feed_url, query_label)

        new_count = 0
        for art in articles:
            url = art["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(art)
                new_count += 1

        print(f"    -> Extracted {new_count} unique articles")
        time.sleep(1.0)  # Polite delay between RSS requests

    print(f"\n  Total RSS articles collected: {len(all_articles)}")
    return all_articles


def load_manual_csv(filepath: str) -> list:
    """Load manually compiled accident articles from a CSV file."""
    if not os.path.exists(filepath):
        print(f"  [!] CSV file not found: {filepath}")
        return []

    articles = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            article = {
                "url": row.get("url", row.get("source_url", f"manual://{uuid.uuid4()}")),
                "title": row.get("title", ""),
                "date_published": row.get("date", row.get("date_published", "")),
                "body_text": row.get("text", row.get("body_text", "")),
                "raw_html": "",
                "source": row.get("source", "manual_import"),
                "query": "manual_csv",
                "scraped_at": datetime.now().isoformat(),
            }
            articles.append(article)

    print(f"  Loaded {len(articles)} manual articles from CSV")
    return articles


def save_articles(articles: list, filepath: str = None) -> str:
    """Merge and save articles to JSON file."""
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "articles_raw.json")

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    existing_articles = []
    seen_urls = set()

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
                for a in existing_articles:
                    seen_urls.add(a["url"])
        except Exception:
            existing_articles = []

    new_articles = []
    for a in articles:
        if a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            new_articles.append(a)

    combined = existing_articles + new_articles

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"\n  SAVED: {len(new_articles)} new articles ({len(combined)} total)")
    print(f"  File: {filepath}")
    return filepath
