from src.scraping.sites.KP.scraper import *

def test_listing_scroll_loads_all(driver, wait):
    #1차

    #2차
    ids = fetch_all_pages_set()
    assert len(ids) >= 10
    assert len(ids) == len(set(ids))