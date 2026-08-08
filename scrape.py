"""Fetch The Hindu headlines and save them as JSON.

Dependencies:
    pip install -r requirements.txt

Run:
    python scrape.py
"""

import json
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

URL = "https://www.thehindu.com/"
OUTPUT_FILE = "Headlines.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}


def fetch_headlines():
    """Fetch headline text and links from The Hindu homepage."""
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []
    seen = set()

    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        link = tag.find("a", href=True)
        if not link:
            continue

        title = link.get_text(" ", strip=True)
        href = link["href"].strip()

        if not title or len(title) < 10 or title in seen:
            continue

        if href.startswith("/"):
            href = "https://www.thehindu.com" + href

        if not href.startswith("http"):
            continue

        seen.add(title)
        headlines.append({"title": title, "url": href})

    return headlines


def save_to_json(headlines):
    """Save headlines to Headlines.json."""
    data = {
        "source": URL,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(headlines),
        "headlines": headlines,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    try:
        headlines = fetch_headlines()

        if not headlines:
            raise RuntimeError("No headlines were found on The Hindu homepage.")

        save_to_json(headlines)

        print(f"Fetched {len(headlines)} headlines.")
        print(f"Saved results to {OUTPUT_FILE}")

        for index, headline in enumerate(headlines, start=1):
            print(f"{index}. {headline['title']}")

        return 0

    except requests.RequestException as exc:
        print(f"ERROR: Unable to fetch The Hindu: {exc}")
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
