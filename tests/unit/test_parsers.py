from pathlib import Path
from src.scraping.sites.kakaopage.parser import parse_detail


def test_parse_detail_from_fixture():
    html = Path("tests/unit/fixtures/detail_sample.html").read_text(encoding="utf-8")
    data = parse_detail(html)
    assert data["title"]
    assert data["age_rating"] in {"ALL","12","15","18"}