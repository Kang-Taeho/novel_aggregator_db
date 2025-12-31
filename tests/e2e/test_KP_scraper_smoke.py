import re
import pytest
import time
from src.scraping.sites.KP import scraper

@pytest.mark.kp_slow
def test_fetch_all_pages_smoke_test(monkeypatch):
    """
    진짜 카카오페이지에 붙어서 ID가 실제로 나오는지 확인하는 스모크 테스트.
    - GENRE_URLS 를 1개 정도로 줄여서 실행하는 걸 추천.
    """
    # 스크롤 두 번만 내리기
    def fake_scroll_to_bottom(*args,**kw):
        drv = args[0]
        for _ in range(2) :
            drv.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.3)
    monkeypatch.setattr("src.scraping.sites.KP.scraper._scroll_to_bottom",fake_scroll_to_bottom)

    # 1가지 장르만 테스트
    scraper.GENRE_URLS = {"wuxia" : "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=87"}

    ids = scraper.fetch_all_pages_set()

    # 최소 몇 개는 나와야 한다
    assert len(ids) > 50
    # ID 형식이 숫자인지 간단 확인
    assert all(re.fullmatch(r"\d+", s) for s in ids)
