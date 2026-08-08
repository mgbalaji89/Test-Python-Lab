# Test-Python-Lab

A hands-on Python learning repository focused on building a strong foundation for automation testing, scripting, and DevOps.

## Objectives

- Learn Python fundamentals
- Practice object-oriented programming
- Work with files and JSON
- Exception handling
- API automation
- Database connectivity
- Unit testing with pytest
- Automation utilities
- Web scraping with Python libraries from pip

## Example: Fetch headlines from The Hindu

This example uses `requests` + `beautifulsoup4` to fetch and print the latest headlines from The Hindu homepage.

### Install dependencies

```bash
pip install requests beautifulsoup4
```

### Python script

Create a file like `the_hindu_headlines.py`:

```python
import requests
from bs4 import BeautifulSoup

URL = "https://www.thehindu.com/"


def fetch_headlines(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    # Collect headlines from common heading tags
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text and text not in headlines:
            headlines.append(text)

    return headlines


if __name__ == "__main__":
    try:
        headlines = fetch_headlines(URL)
        print("The Hindu Headlines:\n")
        for i, headline in enumerate(headlines[:20], start=1):
            print(f"{i}. {headline}")
    except requests.RequestException as exc:
        print(f"Failed to fetch headlines: {exc}")
```

## Project Structure

```text
Test-Python-Lab/
├── basics/
├── oops/
├── collections/
├── exceptions/
├── file_handling/
├── json/
├── api/
├── database/
├── pytest/
├── utilities/
└── README.md
```

## Prerequisites

- Python 3.12+
- VS Code or PyCharm
- Git

## Installation

```bash
git clone https://github.com/mgbalaji89/Test-Python-Lab.git
cd Test-Python-Lab
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python filename.py
```

Or run the scraper example:

```bash
python the_hindu_headlines.py
```

## Future Topics

- Selenium with Python
- Playwright with Python
- REST API Testing
- Pytest Framework
- Logging
- Docker
- GitHub Actions CI/CD

## Author

**Balaji M G**

Learning Python for Automation Testing, DevOps, and AI.
