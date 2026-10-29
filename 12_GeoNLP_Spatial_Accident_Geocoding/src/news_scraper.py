"""
news_scraper.py
===============
Stage 1: Scrapes Ghanaian news websites for road accident articles.
Targets: Citinewsroom, MyJoyOnline, Graphic Online, GhanaWeb, ModernGhana.
Outputs raw articles as structured JSON.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from urllib.parse import urljoin, quote_plus

# ── Configuration ─────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
DELAY_SECONDS = 2  # Polite delay between requests
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ── News Source Definitions ───────────────────────────────────────────────

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

# Search queries to maximize coverage
SEARCH_QUERIES = [
    "road accident",
    "road crash",
    "fatal accident",
    "accident killed",
    "trotro accident",
    "truck accident",
    "pedestrian knocked",
]


SESSION = requests.Session()

def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a page and return parsed BeautifulSoup object."""
    try:
        response = SESSION.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        try:
            return BeautifulSoup(response.text, "lxml")
        except Exception:
            return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [!] Failed to fetch {url}: {e}")
        return None


def extract_article_links(soup: BeautifulSoup, source_config: dict, base_url: str) -> list:
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

        # Get date if available
        date_tag = container.select_one(source_config["date_selector"])
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        datetime_attr = date_tag.get("datetime", "") if date_tag else ""

        articles.append({
            "title": title,
            "url": urljoin(base_url, href),
            "date": datetime_attr or date_str,
        })

    return articles


def fetch_article_body(url: str, body_selectors: list) -> str:
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
                if len(text) > 30:  # Filter out short junk
                    paragraphs.append(text)
            if paragraphs:
                return " ".join(paragraphs)

    # Fallback: grab all <p> tags
    p_tags = soup.find_all("p")
    valid_texts = []
    for p in p_tags:
        text = p.get_text(strip=True)
        if len(text) > 30:
            valid_texts.append(text)
    body = " ".join(valid_texts)
    return body


def is_relevant(title: str, body: str) -> bool:
    """Check if an article is actually about a road accident."""
    combined = (title + " " + body).lower()
    accident_keywords = [
        "accident", "crash", "collision", "killed", "fatal",
        "knocked", "road", "highway", "motorway", "vehicle",
        "truck", "trotro", "bus", "pedestrian", "injured"
    ]
    return sum(1 for kw in accident_keywords if kw in combined) >= 2


def scrape_source(source_key: str, query: str, max_pages: int = 3) -> list:
    """Scrape a single news source for accident articles."""
    config = NEWS_SOURCES[source_key]
    all_articles = []
    seen_urls = set()

    print(f"\n{'='*60}")
    print(f"  Scraping: {config['name']}")
    print(f"  Query: '{query}' | Pages: {max_pages}")
    print(f"{'='*60}")

    for page in range(1, max_pages + 1):
        url = config["search_url"].format(
            query=quote_plus(query),
            page=page
        )
        print(f"  [Page {page}] {url}")

        soup = fetch_page(url)
        if not soup:
            continue

        article_links = extract_article_links(soup, config, url)
        print(f"  [Page {page}] Found {len(article_links)} article links")

        for article_info in article_links:
            if article_info["url"] in seen_urls:
                continue
            seen_urls.add(article_info["url"])

            time.sleep(DELAY_SECONDS)

            print(f"    → Fetching: {article_info['title'][:60]}...")
            body = fetch_article_body(article_info["url"], config["body_selectors"])

            if body and is_relevant(article_info["title"], body):
                all_articles.append({
                    "title": article_info["title"],
                    "url": article_info["url"],
                    "date": article_info["date"],
                    "body": body[:3000],  # Cap body length
                    "source": config["name"],
                    "source_type": "news_scraper",
                    "scraped_at": datetime.now().isoformat(),
                })
                print(f"    ✓ Relevant article saved")
            else:
                print(f"    ✗ Not relevant or empty body")

    return all_articles


def scrape_all_sources(
    sources: list = None,
    queries: list = None,
    max_pages: int = 3
) -> list:
    """
    Scrape all configured news sources.

    Args:
        sources: List of source keys to scrape. None = all sources.
        queries: List of search queries. None = default queries.
        max_pages: Number of search result pages per query per source.

    Returns:
        List of article dictionaries.
    """
    if sources is None:
        sources = list(NEWS_SOURCES.keys())
    if queries is None:
        queries = SEARCH_QUERIES

    all_articles = []
    seen_urls = set()

    for source_key in sources:
        if source_key not in NEWS_SOURCES:
            print(f"[!] Unknown source: {source_key}, skipping.")
            continue

        for query in queries:
            articles = scrape_source(source_key, query, max_pages)
            for article in articles:
                if article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    all_articles.append(article)

    return all_articles


def save_articles(articles: list, filepath: str = None):
    """Save scraped articles to JSON."""
    if filepath is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, "articles_raw.json")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    # Load existing articles if file exists
    existing = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            print(f"  [!] Failed to parse existing JSON in {filepath}. Starting fresh.")

    # Merge (avoid duplicates by URL)
    existing_urls = {a["url"] for a in existing}
    new_articles = [a for a in articles if a["url"] not in existing_urls]

    combined = existing + new_articles
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  SAVED: {len(new_articles)} new articles ({len(combined)} total)")
    print(f"  File: {filepath}")
    print(f"{'='*60}")

    return combined


# ── Main Entry Point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Ghanaian news sites for road accident articles.")
    parser.add_argument("--sources", nargs="+", default=None,
                        choices=list(NEWS_SOURCES.keys()),
                        help="News sources to scrape (default: all)")
    parser.add_argument("--queries", nargs="+", default=None,
                        help="Search queries (default: built-in list)")
    parser.add_argument("--pages", type=int, default=2,
                        help="Number of search result pages per query (default: 2)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file path")

    args = parser.parse_args()

    print("\n" + "█" * 60)
    print("  GHANA ROAD ACCIDENT NEWS SCRAPER")
    print("  Stage 1 of the Accident Map Pipeline")
    print("█" * 60)

    articles = scrape_all_sources(
        sources=args.sources,
        queries=args.queries,
        max_pages=args.pages
    )

    save_articles(articles, args.output)
