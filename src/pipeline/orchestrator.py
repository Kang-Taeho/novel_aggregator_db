from __future__ import annotations
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib import import_module
import logging
from time import perf_counter

from src.pipeline.normalize import map_age, map_status, map_num
from src.data.database import SessionLocal
from src.data.mongo import upsert_meta
from src.data.repository import upsert_canonical_novel, upsert_novel_source

log = logging.getLogger(__name__)

def _db_process(
    p_no: str,
    platform: str,
    scraper,
    parser) -> dict:
    """
    단일 작품 처리 워커:
    - fetch_detail
    - parse_detail
    - normalize
    - Mongo upsert
    - MySQL upsert
    각 워커는 독립적인 Session을 사용해야 한다.
    """
    t0 = perf_counter()
    session = SessionLocal()
    try:
        html = scraper.fetch_detail(p_no)
        t_fetch = perf_counter()
        data = parser.parse_detail(html)
        t_parse = perf_counter()

        if not data.get("platform_item_id"):
            return {
                "p_no": p_no,
                "skipped": True,
                "fetch_ms": int((t_fetch - t0) * 1000),
                "parse_ms": int((t_parse - t_fetch) * 1000),
            }

        age = map_age(data.get("age_rating"))
        status = map_status(data.get("completion_status"))
        view_count = map_num(data.get("view_count"))
        episode_count = map_num(data.get("episode_count"))

        mongo_id = upsert_meta(
            title=data.get("title"),
            author_name=data.get("author_name"),
            description=data.get("description"),
            keywords=data.get("keywords") or [],
        )
        novel_id = upsert_canonical_novel(session, {
            "title": data.get("title"),
            "author_name": data.get("author_name"),
            "genre": data.get("genre"),
            "age_rating": age,
            "completion_status": status,
            "mongo_doc_id": mongo_id,
        })
        upsert_novel_source(session, novel_id, platform, {
            "platform_item_id": data.get("platform_item_id") or p_no,
            "episode_count": episode_count,
            "first_episode_date": data.get("first_episode_date"),
            "view_count": view_count,
        })
        session.commit()
        return {
            "p_no": p_no,
            "ok" : True,
            "skipped": False,
            "fetch_ms": int((t_fetch - t0) * 1000),
            "parse_ms": int((t_parse - t_fetch) * 1000),
        }

    except Exception as e:
        session.rollback()
        log.exception("[%s] FAIL p_no=%s", platform, p_no)
        return {
            "p_no": p_no,
            "ok": False,
            "error": str(e),
        }
    finally:
        session.close()

def _run(
        platform: str,
        sc_fn_name: str,
        max_workers: int = 16) -> dict:
    """
    멀티쓰레드 버전:
    - scraper.fetch_all_pages_set() (또는 다른 sc_fn) 으로 ID 리스트 수집
    - ThreadPoolExecutor로 각 ID를 병렬 처리
    """
    scraper = import_module(f"src.scraping.sites.{platform}.scraper")
    parser = import_module(f"src.scraping.sites.{platform}.parser")
    sc_fn = getattr(scraper, sc_fn_name)

    all_ids = sc_fn()
    process_total = len(all_ids)

    process_ok = process_failed = 0
    skipped = 0
    errors = []
    t_start = perf_counter()

    log.info("[%s] starting MT run: total=%d, workers=%d", platform, process_total, max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {
            ex.submit(_db_process, p_no, platform, scraper, parser): p_no
            for p_no in all_ids
        }
        # log 정보 코드 (기능과 무관)
        for fut in as_completed(futs):
            p_no = futs[fut]
            try:
                result = fut.result()
            except Exception as e:
                process_failed += 1
                if len(errors) < 10:
                    errors.append({"url": f"{platform}{p_no}", "error": str(e)})
                log.exception("[%s] worker crashed p_no=%s", platform, p_no)
                continue

            if result.get("skipped"):
                skipped += 1
                continue

            if result.get("ok"):
                process_ok += 1
                log.info("[%s] OK p_no=%s fetch=%dms parse=%dms",platform,p_no,
                    result.get("fetch_ms", -1),
                    result.get("parse_ms", -1),
                )
            else:
                process_failed += 1
                if len(errors) < 10:
                    errors.append({"url": f"{platform}{p_no}", "error": result.get("error", "")})
                log.warning(
                    "[%s] FAIL p_no=%s error=%s",platform,p_no,
                    result.get("error", ""),
                )

    duration_ms = int((perf_counter() - t_start) * 1000)
    log.info(
        "[%s] MT done: total=%d ok=%d failed=%d skipped=%d duration=%dms",
        platform, process_total, process_ok, process_failed, skipped, duration_ms
    )

    return {
        "platform": platform,
        "sc_fn": sc_fn_name,
        "total": process_total,
        "success": process_ok,
        "failed": process_failed,
        "skipped": skipped,
        "errors_sample": errors,
        "duration_ms": duration_ms,
    }

def run_initial_full(platform: str, max_workers: int = 16) -> dict:
    return _run( platform, "fetch_all_pages_set",max_workers)

# 하루마다 스케쥴 기능 보류
# def run_daily_platform(platform: str, max_workers: int = 16) -> dict:
#     return _run(session, platform, "fetch_top500_pages_list")