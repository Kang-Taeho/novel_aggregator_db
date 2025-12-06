# tests/integration/test_repository_upsert.py
from src.data.database import SessionLocal
from src.data.repository import upsert_canonical_novel, upsert_novel_source
from sqlalchemy import text

def test_upsert_uniqueness():
    s = SessionLocal()
    try:
        nid = upsert_canonical_novel(s, {
            "title": "중복 테스트",
            "author_name": "홍길동",
            "genre": "fantasy",
            "age_rating": "ALL",
            "completion_status": "unknown",
            "mongo_doc_id": None,
        })
        s.commit()

        nid2 = upsert_canonical_novel(s, {
            "title": "중복 테스트",
            "author_name": "홍길동",
            "genre": "fantasy",
            "age_rating": "ALL",
            "completion_status": "unknown",
            "mongo_doc_id": None,
        })
        s.commit()

        assert nid == nid2

        nid3 = upsert_novel_source(s, nid, "KP", {
            "platform_item_id": "123",
            "episode_count": 123,
            "first_episode_date": None,
            "view_count": 0,
        })
        s.commit()

        # 같은 platform/platform_item_id로 업데이트 시도
        nid4 = upsert_novel_source(s, nid, "KP", {
            "platform_item_id": "123",
            "episode_count": 123,
            "first_episode_date": None,
            "view_count": 10,
        })
        s.commit()

        assert nid3 == nid4
        # 테스트 기록 지우기
        s.execute(text("DELETE FROM novel_sources WHERE platform_item_id=123 AND episode_count=123"))
        s.execute(text("DELETE FROM novels WHERE title='중복 테스트' AND author_name='홍길동'"))
        s.commit()
    finally:
        s.close()
