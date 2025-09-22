from src.scraping.sites.kakaopage.parser import parse_detail
from src.pipeline.normalize import map_age, map_status, map_view

SAMPLE_DETAIL_URL = [
    "https://page.kakao.com/content/67404682", #15세,UP,키워드
    "https://page.kakao.com/content/67672088", #신작,키워드
    "https://page.kakao.com/content/59137406", #키워드x
    "https://page.kakao.com/content/66943643", #단행본/완결
    "https://page.kakao.com/content/57429506", #휴재
    "https://page.kakao.com/content/57948732", #억조회수
]

def test_parse_detail_from_fixture():
    for i in SAMPLE_DETAIL_URL :
        data = parse_detail(i)
        assert data["title"]
        assert data["keywords"] or data["keywords"] is None
        assert map_age(data["age_rating"]) in {"ALL","12","15","18"}
        assert map_status(data["completion_status"]) in {"ongoing","completed","hiatus"}
        assert type(map_view(data["view_count"])) == int
        assert type(map_view(data["episode_count"])) == int