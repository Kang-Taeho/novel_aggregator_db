from src.scraping.sites.NS.parser import parse_detail
from src.scraping.sites.NS.scraper import fetch_detail

SAMPLE_DETAIL_URL = [
    fetch_detail("https://series.naver.com/novel/detail.series?productNo=12450709"),
    fetch_detail("https://series.naver.com/novel/detail.series?productNo=9650202"),
]

def test_parse_detail():
    for i in SAMPLE_DETAIL_URL :
        data = parse_detail(i)
        assert data["title"], f"title missing. Extracted keys: {data}"
        assert data["author_name"], f"author missing. Extracted keys: {data}"
        assert data["genre"], f"genre missing. Extracted keys: {data}"
        assert data["completion_status"], f"status missing. Extracted keys: {data}"
        assert data["description"], f"description missing. Extracted keys: {data}"