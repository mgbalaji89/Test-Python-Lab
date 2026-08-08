"""Scrape Tamil news headlines and build a self-contained HTML report.

Sources:
- Dinamalar: https://www.dinamalar.com/
- Daily Thanthi: https://www.dailythanthi.com/

Dependencies:
    pip install -r requirements.txt

Run:
    python scrape_tamil_news.py
"""

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

SOURCES = {
    "Dinamalar": "https://www.dinamalar.com/",
    "Daily Thanthi": "https://www.dailythanthi.com/",
}

OUTPUT_FILE = Path("tamil_news_report.html")
MAX_HEADLINES = 30
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ta-IN,ta;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

# These are navigation/UI labels rather than news headlines.
EXCLUDED_TEXT = {
    "read more",
    "read more >>",
    "visit site",
    "home",
    "login",
    "subscribe",
    "subscription",
    "live",
    "podcast",
    "video",
    "photos",
}


def is_tamil_text(text: str) -> bool:
    """Return True when text contains at least one Tamil Unicode character."""
    return any("\u0b80" <= char <= "\u0bff" for char in text)


def is_candidate_link(base_url: str, href: str, title: str) -> bool:
    """Filter navigation, external links and obviously non-story links."""
    if not href or not title or len(title) < 8:
        return False

    normalized_title = " ".join(title.split()).strip().lower()
    if normalized_title in EXCLUDED_TEXT:
        return False

    # Prefer Tamil headlines. This also removes most English navigation text.
    if not is_tamil_text(title):
        return False

    absolute_url = urljoin(base_url, href)
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(absolute_url)

    if parsed_url.scheme not in {"http", "https"}:
        return False

    # Only collect stories belonging to the publisher's domain.
    if parsed_url.netloc != parsed_base.netloc:
        return False

    # Ignore the homepage and obvious non-story utility links.
    if parsed_url.path in {"", "/"}:
        return False

    ignored_parts = {
        "/search",
        "/login",
        "/subscribe",
        "/subscription",
        "/contact",
        "/privacy",
        "/terms",
    }
    if any(parsed_url.path.rstrip("/").lower().startswith(part) for part in ignored_parts):
        return False

    return True


def fetch_headlines(source_name: str, url: str):
    """Fetch unique headline/link pairs from a news homepage.

    The previous implementation only inspected h1-h4 tags. Both publishers
    currently expose many article titles as ordinary anchor elements, so the
    scraper now uses anchors as a fallback and filters them by domain/title.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    response.raise_for_status()

    print(
        f"{source_name}: HTTP {response.status_code}, "
        f"final URL={response.url}, HTML={len(response.text):,} bytes"
    )

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []
    seen = set()

    # First prefer semantic heading links where available.
    candidates = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        link = tag.find("a", href=True) or (tag if tag.name == "a" else None)
        if link:
            candidates.append(link)

    # Current versions of the sites also render many article titles as plain
    # <a> elements, so inspect anchors when heading extraction is insufficient.
    if len(candidates) < MAX_HEADLINES:
        candidates.extend(soup.find_all("a", href=True))

    for link in candidates:
        title = link.get_text(" ", strip=True)
        href = link.get("href", "").strip()

        if not is_candidate_link(url, href, title):
            continue

        absolute_url = urljoin(url, href)
        key = (title, absolute_url)
        if key in seen:
            continue

        seen.add(key)
        headlines.append({"title": title, "url": absolute_url})

        if len(headlines) >= MAX_HEADLINES:
            break

    print(f"{source_name}: extracted {len(headlines)} headline candidates")
    return headlines


def render_source_card(source_name: str, url: str, headlines: list[dict]):
    items = "\n".join(
        f'<li><a href="{escape(item["url"], quote=True)}" '
        f'target="_blank" rel="noopener noreferrer">'
        f'{escape(item["title"])}</a></li>'
        for item in headlines
    )

    if not items:
        items = '<li class="empty">No headlines were captured.</li>'

    return f"""
    <section class="source-card">
        <div class="source-header">
            <div>
                <h2>{escape(source_name)}</h2>
                <p>{len(headlines)} headlines captured</p>
            </div>
            <a class="source-link" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Visit site ↗</a>
        </div>
        <ol>{items}</ol>
    </section>
    """


def build_report(results: dict, errors: dict):
    fetched_at = datetime.now(timezone.utc).astimezone().strftime(
        "%d %b %Y, %I:%M:%S %p %Z"
    )
    total = sum(len(items) for items in results.values())

    cards = []
    for source_name, url in SOURCES.items():
        cards.append(render_source_card(source_name, url, results.get(source_name, [])))

    error_html = ""
    if errors:
        error_items = "".join(
            f"<li><strong>{escape(name)}:</strong> {escape(message)}</li>"
            for name, message in errors.items()
        )
        error_html = (
            '<div class="warning"><strong>Source warnings</strong>'
            f"<ul>{error_items}</ul></div>"
        )

    return f"""<!DOCTYPE html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tamil News Headlines Report</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #f4f7fb; color: #172033; }}
.container {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 50px; }}
.hero {{ background: linear-gradient(135deg, #172554, #0f766e); color: white; border-radius: 20px; padding: 30px; box-shadow: 0 12px 30px rgba(15, 23, 42, .15); }}
.hero h1 {{ margin: 0 0 8px; font-size: clamp(28px, 5vw, 44px); }}
.hero p {{ margin: 6px 0; opacity: .9; }}
.stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px; }}
.stat {{ background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.18); border-radius: 12px; padding: 12px 16px; min-width: 150px; }}
.stat strong {{ display: block; font-size: 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 24px; }}
.source-card {{ background: white; border-radius: 18px; padding: 22px; box-shadow: 0 7px 22px rgba(15,23,42,.08); border: 1px solid #e5e7eb; }}
.source-header {{ display: flex; justify-content: space-between; gap: 16px; align-items: start; border-bottom: 1px solid #e5e7eb; padding-bottom: 14px; }}
.source-header h2 {{ margin: 0; font-size: 24px; }}
.source-header p {{ margin: 5px 0 0; color: #64748b; }}
.source-link {{ text-decoration: none; font-weight: 700; white-space: nowrap; }}
ol {{ padding-left: 26px; margin-bottom: 0; }}
li {{ padding: 10px 0; line-height: 1.65; }}
li a {{ color: #1d4ed8; text-decoration: none; }}
li a:hover {{ text-decoration: underline; }}
.empty {{ color: #b91c1c; }}
.warning {{ margin-top: 20px; padding: 16px 18px; border-radius: 14px; background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; }}
.footer {{ margin-top: 24px; text-align: center; color: #64748b; font-size: 13px; }}
@media (max-width: 600px) {{ .hero {{ padding: 22px; }} .source-header {{ flex-direction: column; }} }}
</style>
</head>
<body>
<main class="container">
<header class="hero">
    <h1>தமிழ் செய்தி தலைப்புகள்</h1>
    <p>Dinamalar + Daily Thanthi — automated headline collection</p>
    <p>Generated: {escape(fetched_at)}</p>
    <div class="stats">
        <div class="stat"><strong>{total}</strong>Total headlines</div>
        <div class="stat"><strong>{len(results.get("Dinamalar", []))}</strong>Dinamalar</div>
        <div class="stat"><strong>{len(results.get("Daily Thanthi", []))}</strong>Daily Thanthi</div>
    </div>
</header>
{error_html}
<div class="grid">
{''.join(cards)}
</div>
<footer class="footer">Generated by Test-Python-Lab • Source links point to the original publishers.</footer>
</main>
</body>
</html>
"""


def main():
    results = {}
    errors = {}

    for source_name, url in SOURCES.items():
        try:
            results[source_name] = fetch_headlines(source_name, url)
            print(f"{source_name}: {len(results[source_name])} headlines")
        except requests.RequestException as exc:
            results[source_name] = []
            errors[source_name] = f"Request failed: {exc}"
            print(f"{source_name}: request failed - {exc}")
        except Exception as exc:
            results[source_name] = []
            errors[source_name] = f"Unexpected error: {exc}"
            print(f"{source_name}: unexpected error - {exc}")

    report = build_report(results, errors)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Report written to {OUTPUT_FILE}")

    if not any(results.values()):
        raise SystemExit("No headlines were captured from either source.")


if __name__ == "__main__":
    main()
