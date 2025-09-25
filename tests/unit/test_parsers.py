from src.scraping.sites.kakaopage.parser import parse_detail
from scraping.sites.kakaopage.scraper import fetch_detail

SAMPLE_DETAIL_URL = [
    fetch_detail("https://page.kakao.com/content/67404682"), #15세
    fetch_detail("https://page.kakao.com/content/67672088"), #신작,키워드
    fetch_detail("https://page.kakao.com/content/66943643"), #단행본/완결
    fetch_detail("https://page.kakao.com/content/57429506"), #휴재
    fetch_detail("https://page.kakao.com/content/57948732"), #억조회수
    # fetch_detail("https://page.kakao.com/content/1234567"),  #판매중지작품
]

def test_parse_detail():
    for i in SAMPLE_DETAIL_URL :
        data = parse_detail(i)
        assert data["title"]
        assert data["author_name"]
        assert data["genre"]
        assert data["first_episode_date"]
        assert data["episode_count"]