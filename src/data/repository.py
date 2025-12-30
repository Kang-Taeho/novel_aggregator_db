from sqlalchemy.orm import Session
from sqlalchemy import text, select, func
from sqlalchemy.dialects.mysql import insert as mysql_insert
from src.data import models

def get_platform_id(session: Session, slug: str) -> int:
    """
    주어진 플랫폼 slug에 해당하는 platform.id 를 반환한다.
    """
    q = select(models.Platform.id).where(models.Platform.slug == slug)
    pid = session.execute(q).scalar_one_or_none()
    if pid is None: raise ValueError(f"Unknown platform slug: {slug}")
    return int(pid)

def upsert_canonical_novel(session: Session, data: dict) -> int:
    """
        Novel 테이블에 novel 데이터를 UPSERT(삽입 or 업데이트) 한다.
        - UNIQUE KEY 충돌 시 update 수행
        - insert 시 lastrowid 반환
        - update 시 동일 novel을 다시 SELECT 하여 id 반환
    """
    stmt = mysql_insert(models.Novel).values(
        title=data["title"],
        author_name=data.get("author_name"),
        genre=data.get("genre"),
        age_rating=data.get("age_rating","ALL"),
        completion_status=data.get("completion_status","unknown"),
        mongo_doc_id=data.get("mongo_doc_id"),
    )
    stmt = stmt.on_duplicate_key_update(
        age_rating=stmt.inserted.age_rating,
        completion_status=stmt.inserted.completion_status,
        mongo_doc_id=stmt.inserted.mongo_doc_id,
        updated_at = func.now(),
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
    """
       NovelSource 테이블에 novel source 정보를 UPSERT 한다.
       - UNIQUE KEY 충돌 시 update 수행
       - INSERT 시 lastrowid 반환
       - UPDATE 시 0 반환
    """
    platform_id = get_platform_id(session, platform_slug)
    stmt = mysql_insert(models.NovelSource).values(
        novel_id=novel_id,
        platform_id=platform_id,
        platform_item_id=data["platform_item_id"],
        episode_count=data.get("episode_count"),
        first_episode_date=data.get("first_episode_date"),
        view_count=data.get("view_count"),
    )
    stmt = stmt.on_duplicate_key_update(
        episode_count=stmt.inserted.episode_count,
        first_episode_date=stmt.inserted.first_episode_date,
        view_count=stmt.inserted.view_count,
    )
    res = session.execute(stmt)
    return int(res.lastrowid or 0)
