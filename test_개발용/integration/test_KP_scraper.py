# test_개발용/selenium/test_KP_scraper.py
import re
import pytest
from src.scraping.sites.KP import scraper

@pytest.mark.kp_slow
def test_fetch_all_pages_set_live_minimal():
    """
    진짜 카카오페이지에 붙어서 ID가 실제로 나오는지 확인하는 느린 테스트.
    - GENRE_URLS 를 1개 정도로 줄여서 실행하는 걸 추천.
    """
    # 필요하다면 테스트 안에서 GENRE_URLS 축소
    # scraper.GENRE_URLS[:] = scraper.GENRE_URLS[4:5]
    ids = scraper.fetch_all_pages_set()

    # 최소 몇 개는 나와야 한다
    assert len(ids) > 50000
    # ID 형식이 숫자인지 간단 확인
    assert all(re.fullmatch(r"\d+", s) for s in ids)
