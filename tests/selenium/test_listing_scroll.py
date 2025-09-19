def test_listing_scroll_loads_all(driver, wait):
    from .pages.listing_page import ListingPage
    p = ListingPage(driver, wait)
    p.open(); p.load_all()
    ids = p.series_ids()
    assert len(ids) >= 10
    assert len(ids) == len(set(ids))