from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from importlib import import_module
from src.pipeline.normalize import map_age, map_status
from src.data.mongo import upsert_meta
from src.data.repository import upsert_canonical_novel, upsert_novel_source

def run(session: Session, platform: str, scope: str = "incremental", since: datetime | None = None) -> dict:
    scraper = import_module(f"src.scraping.sites.{platform}.scraper")
    parser = import_module(f"src.scraping.sites.{platform}.parser")
    processed = 0
    for url in list(scraper.list_updated(since)):
        html = scraper.fetch_detail(url)
        data = parser.parse_detail(html)
        age = map_age(data.get("age_rating"))
        status = map_status(data.get("completion_status"))
        mongo_id = upsert_meta(
            title=data.get("title",""),
            author_name=data.get("author_name"),
            description=data.get("description"),
            keywords=data.get("keywords") or [],
            mongo_doc_id=data.get("mongo_doc_id"),
        )
        novel_id = upsert_canonical_novel(session, {
            "title": data.get("title",""),
            "author_name": data.get("author_name"),
            "age_rating": age,
            "completion_status": status,
            "mongo_doc_id": mongo_id,
        })
        upsert_novel_source(session, novel_id, platform, {
            "platform_item_id": data.get("platform_item_id",""),
            "episode_count": data.get("episode_count"),
            "last_episode_date": data.get("last_episode_date"),
            "view_count": data.get("view_count"),
            "source_url": data.get("source_url", url),
        })
        session.commit()
        processed += 1
    return {"processed": processed}
