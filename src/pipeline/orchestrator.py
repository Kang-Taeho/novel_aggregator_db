from __future__ import annotations
from sqlalchemy.orm import Session
from importlib import import_module
import logging
from time import perf_counter
from src.pipeline.normalize import map_age, map_status
from src.data.mongo import upsert_meta
from src.data.repository import upsert_canonical_novel, upsert_novel_source

log = logging.getLogger(__name__)

def _run(session: Session, platform: str, list_fn_name: str, commit_every: int = 20) -> dict:
    scraper = import_module(f"src.scraping.sites.{platform}.scraper")
    parser = import_module(f"src.scraping.sites.{platform}.parser")
    list_fn = getattr(scraper, list_fn_name)
    urls = list_fn()

    process_total = len(urls)
    process_ok = process_failed = 0
    errors = []
    t_start = perf_counter()

    for index, url in enumerate(urls, 1):
        t0 = perf_counter()
        try :
            html = scraper.fetch_detail(url)
            t_fetch = perf_counter()
            data = parser.parse_detail(html)
            t_parse = perf_counter()

            age = map_age(data.get("age_rating"))
            status = map_status(data.get("completion_status"))
            mongo_id = upsert_meta(
                title=data.get("title", ""),
                author_name=data.get("author_name"),
                description=data.get("description"),
                keywords=data.get("keywords") or [],
                mongo_doc_id=data.get("mongo_doc_id"),
            )
            novel_id = upsert_canonical_novel(session, {
                "title": data.get("title", ""),
                "author_name": data.get("author_name"),
                "age_rating": age,
                "completion_status": status,
                "mongo_doc_id": mongo_id,
            })
            upsert_novel_source(session, novel_id, platform, {
                "platform_item_id": data.get("platform_item_id", ""),
                "episode_count": data.get("episode_count"),
                "last_episode_date": data.get("last_episode_date"),
                "view_count": data.get("view_count"),
            })

            if (index % commit_every) == 0:
                session.commit()
            process_ok += 1
            log.info(
                "[%s] %d/%d OK fetch=%dms parse=%dms",
                platform, index, process_total,
                int((t_fetch - t0) * 1000), int((t_parse - t_fetch) * 1000)
            ) # 필요 시 사용정보

        except Exception as e :
            session.rollback()
            process_failed += 1
            if len(errors) < 10:
                errors.append({"url": url, "error": str(e)})
            log.exception("[%s] %d/%d FAIL url=%s", platform, index, process_total, url)

    try:
        session.commit()
    except Exception:
        session.rollback()
        log.exception("final commit failed; rolled back")

    return {
        "platform": platform,
        "list_fn": list_fn_name,
        "total": process_total,
        "success": process_ok,
        "failed": process_failed,
        "errors_sample": errors,
        "duration_ms": int((perf_counter() - t_start) * 1000),
    }

def run_initial_full(session: Session, platform: str) -> dict:
    return _run(session, platform, "fetch_all_pages_list")

def run_daily_top500(session: Session, platform: str) -> dict:
    return _run(session, platform, "fetch_top500_pages_list")