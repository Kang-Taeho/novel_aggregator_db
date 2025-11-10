import pytest
from src.scraping.sites.naverseries import scraper

@pytest.mark.naver_live
def test_fetch_all_pages_set_live_smoke(monkeypatch):
    """
    실제 네이버 시리즈에 붙는 스모크 테스트.
    - 너무 자주 돌리지 말 것
    - 결과 개수/형식만 대략 확인
    """
    # 장르 하나만
    monkeypatch.setattr(scraper, "GENRE_CODES", scraper.GENRE_CODES[6:7])
    # 페이지도 2페이지만 보게
    monkeypatch.setattr(scraper, "_total_pages", lambda url: 10)
    ids = scraper.fetch_all_pages_set()

    # 최소 몇 개 이상 나오는지만 느슨하게 체크
    assert len(ids) > 100
    assert all(id_.isdigit() for id_ in ids)
