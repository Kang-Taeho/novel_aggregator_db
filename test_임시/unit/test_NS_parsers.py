from src.scraping.sites.NS.parser import parse_detail
from src.scraping.sites.NS.scraper import fetch_detail
from src.pipeline.schemas import NovelParsed
from src.pipeline.normalize import map_age, map_status, map_num, map_date
import logging

log = logging.getLogger(__name__)
SAMPLE_DETAIL_URL = [
    fetch_detail(12450709),
    fetch_detail(9650202),
]

def test_parse_detail():
    for i in SAMPLE_DETAIL_URL :
        data = parse_detail(i)
        log.info(data)
        data['age_rating'] = map_age(data['age_rating'])
        data['completion_status'] = map_status(data['completion_status'])
        data['view_count'] = map_num( data['view_count'])
        data['episode_count'] = map_num(data['episode_count'])
        data['first_episode_date'] = map_date(data['first_episode_date'])

        assert data["title"]
        assert data["author_name"]
        assert data["genre"]
        assert data["completion_status"]
        assert data["description"]
        assert NovelParsed(**data)