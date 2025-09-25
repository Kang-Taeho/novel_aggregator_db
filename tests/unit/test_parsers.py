from src.scraping.sites.munpia.parser import parse_detail
from scraping.sites.munpia.scraper import fetch_detail

SAMPLE_DETAIL_URL = [
    fetch_detail("https://novel.munpia.com/453239"), #연재
    fetch_detail("https://novel.munpia.com/467924"), #완결
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