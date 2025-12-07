from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib import import_module
import logging
from time import perf_counter

from requests.exceptions import RequestException
from sqlalchemy.exc import OperationalError, InterfaceError
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, NetworkTimeout

from src.core.retry import retry
from src.pipeline.normalize import map_age, map_status, map_num, map_date
from src.pipeline.schemas import NovelParsed
from src.data.database import SessionLocal
from src.data.mongo import upsert_meta
from src.data.repository import upsert_canonical_novel, upsert_novel_source

log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)
RETRY_EXCEPTIONS = (
    RequestException,
    OperationalError,
    InterfaceError,
    AutoReconnect,
    ServerSelectionTimeoutError,
    NetworkTimeout,)

@retry(
    exceptions=RETRY_EXCEPTIONS,
    tries=3, base=1.0, cap=8.0, jitter=0.3,
)
def _db_process(
    p_no: str,
    p_slug: str,
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
        del html

        try :
            data['age_rating'] = map_age(data['age_rating'])
            data['completion_status'] = map_status(data['completion_status'])
            data['view_count'] = map_num(data['view_count'])
            data['episode_count'] = map_num(data['episode_count'])
            data['first_episode_date'] = map_date(data['first_episode_date'])

            obj = NovelParsed(**data)
        except Exception as e: # 예) 19세 이상 소설데이터는 검색 불가
            return {
                "p_no": p_no,
                "skipped": True,
                "fetch_ms": int((t_fetch - t0) * 1000),
                "parse_ms": int((t_parse - t_fetch) * 1000),
            }

        mongo_id = upsert_meta(
            title=obj.title,
            author_name=obj.author_name,
            description=obj.description,
            keywords=obj.keywords,
        )
        novel_id = upsert_canonical_novel(session, {
            "title": obj.title,
            "author_name": obj.author_name,
            "genre": obj.genre,
            "age_rating": obj.age_rating,
            "completion_status": obj.completion_status,
            "mongo_doc_id": mongo_id,
        })
        upsert_novel_source(session, novel_id, p_slug, {
            "platform_item_id": obj.platform_item_id,
            "episode_count": obj.episode_count,
            "first_episode_date": obj.first_episode_date,
            "view_count": obj.view_count,
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
        log.exception("[%s] FAIL p_no=%s", p_slug, p_no)
        return {
            "p_no": p_no,
            "ok": False,
            "error": str(e),
        }
    finally:
        session.close()

def _run(
        p_slug: str,
        sc_fn_name: str,
        max_workers : int) -> dict:
    """
    멀티쓰레드 버전:
    - scraper.fetch_all_pages_set() (또는 다른 sc_fn) 으로 ID 리스트 수집
    - ThreadPoolExecutor로 각 ID를 병렬 처리
    """
    scraper = import_module(f"src.scraping.sites.{p_slug}.scraper")
    parser = import_module(f"src.scraping.sites.{p_slug}.parser")
    sc_fn = getattr(scraper, sc_fn_name)

    all_ids = sc_fn()
    process_total = len(all_ids)

    process_ok = 0
    process_failed = 0
    skipped = 0
    errors = []
    t_start = perf_counter()

    log.info("[%s] starting MT run: total=%d, workers=%d", p_slug, process_total, max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {
            ex.submit(_db_process, p_no, p_slug, scraper, parser): p_no
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
                    errors.append({"url": f"{p_slug}/{p_no}", "error": str(e)})
                log.exception("[%s] worker crashed p_no=%s", p_slug, p_no)
                continue

            if result.get("skipped"):
                skipped += 1
                continue

            if result.get("ok"):
                process_ok += 1
                log.info("[%s] OK p_no=%s fetch=%dms parse=%dms",p_slug,p_no,
                    result.get("fetch_ms", -1),
                    result.get("parse_ms", -1),
                )
            else:
                process_failed += 1
                if len(errors) < 10:
                    errors.append({"url": f"{p_slug}/{p_no}", "error": result.get("error", "")})
                log.warning(
                    "[%s] FAIL p_no=%s error=%s",p_slug,p_no,
                    result.get("error", ""),
                )

    duration_ms = int((perf_counter() - t_start) * 1000)
    log.info(
        "[%s] MT done: total=%d ok=%d failed=%d skipped=%d duration=%dms",
        p_slug, process_total, process_ok, process_failed, skipped, duration_ms
    )

    return {
        "platform_slug": p_slug,
        "sc_fn": sc_fn_name,
        "total": process_total,
        "success": process_ok,
        "failed": process_failed,
        "skipped": skipped,
        "errors_sample": errors,
        "duration_ms": duration_ms,
    }

def run_initial_full(platform_slug: str, max_workers: int = 8) -> dict:
    return _run( platform_slug, "fetch_all_pages_set",max_workers)
