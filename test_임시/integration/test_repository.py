from src.data.database import SessionLocal
from src.data.repository import upsert_novel_source, upsert_canonical_novel
import datetime

novel_data = {
    "title" : "제목1",
    "author_name" : "작가1",
    "age_rating" : "ALL",
    "completion_status" : "unknown",
    "mongo_doc_id" : "1234",
}

novel_source_data = {
    "novel_id" : "1234",
    "platform_id" : "5678",
    "platform_item_id" : "91011",
    "episode_count" : "100",
    "last_episode_date" :  datetime.datetime.now(),
    "view_count" : "9999999"
}


def test_upsert_roundtrip():
    with SessionLocal() as db:
        nid = upsert_canonical_novel(db, novel_data)
        sid = upsert_novel_source(db,nid,"KP", novel_source_data)
        assert isinstance(nid, int) and isinstance(sid, int)