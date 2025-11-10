from src.scraping.sites.naverseries import scraper

def test_fetch_all_pages_set_aggregates_all_ids(monkeypatch):
    # 1) _total_pages: 각 장르 URL 당 3페이지라고 가정
    monkeypatch.setattr(scraper, "_total_pages", lambda url: 3)

    # 2) _fetch_page_ids: page 번호에 따라 다른 id 세트 리턴
    def fake_fetch_page_ids(base_url, page):
        return {f"{base_url[-3:]}-{page}-1", f"{base_url[-3:]}-{page}-2"}

    monkeypatch.setattr(scraper, "_fetch_page_ids", fake_fetch_page_ids)

    ids = scraper.fetch_all_pages_set()

    # GENRE_URLS 수 × 각 3 페이지 × 페이지당 2개
    expected_count = len(scraper.GENRE_CODES) * 3 * 2
    assert len(ids) == expected_count
