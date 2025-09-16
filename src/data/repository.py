from sqlalchemy.orm import Session
from sqlalchemy import text, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from src.data import models
from datetime import datetime, UTC


def get_platform_id(session: Session, slug: str) -> int:
    q = select(models.Platform.id).where(models.Platform.slug == slug)
    pid = session.execute(q).scalar_one_or_none()
    if pid is None: raise ValueError(f"Unknown platform slug: {slug}")
    return int(pid)

def upsert_canonical_novel(session: Session, data: dict) -> int:
    stmt = mysql_insert(models.Novel).values(
        title=data["title"],
        author_name=data.get("author_name"),
        age_rating=data.get("age_rating","ALL"),
        completion_status=data.get("completion_status","unknown"),
        mongo_doc_id=data.get("mongo_doc_id"),
    )
    stmt = stmt.on_duplicate_key_update(
        age_rating=stmt.inserted.age_rating,
        completion_status=stmt.inserted.completion_status,
        mongo_doc_id=stmt.inserted.mongo_doc_id,
        update_at = datetime.now(UTC),
    )
    res = session.execute(stmt)
    rid = res.lastrowid
    if rid: return int(rid)
    q = text("""SELECT id FROM novels
                WHERE normalized_title = LOWER(TRIM(:t))
                  AND normalized_author = LOWER(TRIM(COALESCE(:a,'')))
                LIMIT 1""")
    return int(session.execute(q, {"t": data["title"], "a": data.get("author_name")}).scalar_one())

def upsert_novel_source(session: Session, novel_id: int, platform_slug: str, data: dict) -> int:
    platform_id = get_platform_id(session, platform_slug)
    stmt = mysql_insert(models.NovelSource).values(
        novel_id=novel_id,
        platform_id=platform_id,
        platform_item_id=data["platform_item_id"],
        episode_count=data.get("episode_count"),
        last_episode_date=data.get("last_episode_date"),
        view_count=data.get("view_count"),
    )
    stmt = stmt.on_duplicate_key_update(
        episode_count=stmt.inserted.episode_count,
        last_episode_date=stmt.inserted.last_episode_date,
        view_count=stmt.inserted.view_count,
    )
    res = session.execute(stmt)
    return int(res.lastrowid or 0)
