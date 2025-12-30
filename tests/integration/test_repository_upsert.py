# tests/integration/test_repository_upsert.py
from src.data.database import SessionLocal
from src.data.repository import upsert_canonical_novel, upsert_novel_source
from sqlalchemy import text

def test_upsert_uniqueness():
    """
    repository upsert 기능 통합 테스트

    검증 목표
    ---------
    1) Novel(upsert_canonical_novel)
       - 동일 (title + author_name) 데이터로 여러 번 upsert 호출 시
         새로운 row가 생성되지 않고 같은 id 반환되는지 확인

    2) NovelSource(upsert_novel_source)
       - 동일 (novel_id + platform + platform_item_id) 조건에서 upsert 시
         insert 한 id 와 update 이후 반환 id 가 동일한지 확인
    """
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
