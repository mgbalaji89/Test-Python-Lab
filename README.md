# Test-Python-Lab

A hands-on Python learning repository focused on automation testing, scripting, web scraping, and DevOps.

## Current Automation Examples

### 1. The Hindu headline scraper

`scrape.py` fetches The Hindu headlines and stores them in `Headlines.json`.

### 2. Tamil news headline report

`scrape_tamil_news.py` fetches headlines from:

- [Dinamalar](https://www.dinamalar.com/)
- [Daily Thanthi](https://www.dailythanthi.com/)

It generates a **single self-contained HTML report** named `tamil_news_report.html`. The report contains inline CSS, so it can be opened directly without additional assets.

## Tamil News Report

Run locally:

```bash
python -m pip install -r requirements.txt
python scrape_tamil_news.py
```

Open the generated report:

```text
tamil_news_report.html
```

The report contains:

- Total headline count
- Dinamalar headlines with article links
- Daily Thanthi headlines with article links
- Fetch timestamp
- Source warnings when a site cannot be reached
- Responsive, self-contained HTML/CSS

## GitHub Actions CI/CD

The workflow is located at:

```text
.github/workflows/tamil-news-report.yml
```

Every push to `main` or manual workflow execution performs:

```text
Checkout
   ↓
Python 3.12
   ↓
Install requirements.txt
   ↓
Run scraper
   ↓
Validate tamil_news_report.html
   ↓
Upload HTML artifact
   ↓
Deploy report to GitHub Pages
```

The workflow intentionally fails if neither news source produces headlines or if the generated report is missing/invalid.

## Dependencies

```text
requests
beautifulsoup4
```

Install with:

```bash
pip install -r requirements.txt
```

## Project Structure

```text
Test-Python-Lab/
├── scrape.py
├── scrape_tamil_news.py
├── requirements.txt
├── .github/
│   └── workflows/
│       └── tamil-news-report.yml
└── README.md
```

## Prerequisites

- Python 3.12+
- VS Code or PyCharm
- Git

## Future Topics

- Selenium with Python
- Playwright with Python
- REST API Testing
- Pytest Framework
- Logging
- Docker
- GitHub Actions CI/CD
- Scheduled web-scraping jobs
- Automated HTML reporting

## Author

**Balaji M G**

Learning Python for Automation Testing, DevOps, and AI.
