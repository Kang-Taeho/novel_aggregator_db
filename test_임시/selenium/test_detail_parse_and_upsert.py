# test_detail_parse_and_upsert.py
from src.data.database import SessionLocal
from src.data.repository import upsert_canonical_novel, upsert_novel_source
from src.pipeline.normalize import *
from .pages.detail_page import DetailPage


def test_detail_parse_and_upsert(driver, wait):
    detail_url = "https://example.com/novels/123" # 대상 교체
    page = DetailPage(driver, wait); page.open(detail_url)
    parsed = page.snapshot()
    with SessionLocal() as db:
        nid = upsert_canonical_novel(parsed)
        sid = upsert_novel_source(nid, {"platform_id":"KP","platform_item_id":"series_123","episode_count":parsed.get("episode_count")})
        assert nid > 0 and sid > 0