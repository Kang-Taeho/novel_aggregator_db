# tests/integration/test_repository_upsert.py
from sqlalchemy.orm import Session
from src.data.database import SessionLocal
from src.data.repository import upsert_canonical_novel, upsert_novel_source

def test_upsert_uniqueness():
    s: Session = SessionLocal()
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

        assert nid == nid2, "동일 title/author는 같은 canonical novel 이어야 함"

        nid3 = upsert_novel_source(s, nid, "KP", {
            "platform_item_id": "123",
            "episode_count": 1,
            "first_episode_date": None,
            "view_count": 0,
        })
        s.commit()

        # 같은 platform/platform_item_id로 업데이트 시도
        nid4 = upsert_novel_source(s, nid, "KP", {
            "platform_item_id": "123",
            "episode_count": 2,
            "first_episode_date": None,
            "view_count": 10,
        })
        s.commit()

        assert nid3 == nid4, "동일 title/author는 같은 canonical novel 이어야 함"
    finally:
        s.close()
