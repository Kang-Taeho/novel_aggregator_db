from src.data.database import SessionLocal
from src.data.repository import upsert_novel_source, upsert_canonical_novel


def test_upsert_roundtrip():
    with SessionLocal() as db:
        nid = upsert_canonical_novel({"title":"테스트 소설","author_name":"홍길동","age_rating":"ALL","completion_status":"unknown"})
        sid = upsert_novel_source(nid, {"platform_id":"KP","platform_item_id":"series_123","episode_count":100})
        assert isinstance(nid, int) and isinstance(sid, int)