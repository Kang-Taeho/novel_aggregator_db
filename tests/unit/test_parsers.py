from src.scraping.sites.kakaopage.parser import parse_detail
from scraping.sites.kakaopage.scraper import fetch_detail

SAMPLE_DETAIL_URL = [
    fetch_detail("https://page.kakao.com/content/58474045"),
]

def test_parse_detail():
    for i in SAMPLE_DETAIL_URL :
        data = parse_detail(i)
        assert data["title"], f"title missing. Extracted keys: {data}"
        assert data["author_name"], f"title missing. Extracted keys: {data}"
        assert data["genre"], f"title missing. Extracted keys: {data}"
        assert data["completion_status"], f"title missing. Extracted keys: {data}"
        assert data["first_episode_date"], f"title missing. Extracted keys: {data}"
        assert data["view_count"], f"title missing. Extracted keys: {data}"
        assert data["description"], f"title missing. Extracted keys: {data}"