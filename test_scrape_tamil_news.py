import ast
from pathlib import Path


SCRIPT = Path("scrape_tamil_news.py")


def test_scraper_has_valid_python_syntax():
    ast.parse(SCRIPT.read_text(encoding="utf-8"))


def test_scraper_defines_expected_entry_point():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    assert {"fetch_headlines", "build_report", "main"}.issubset(function_names)
