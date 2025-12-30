from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib import import_module
import logging
from time import perf_counter
from requests.exceptions import RequestException
from sqlalchemy.exc import OperationalError, InterfaceError
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, NetworkTimeout

from src.core.config import settings
from src.core.retry import retry
from src.pipeline.normalize import map_age, map_status, map_num, map_date
from src.pipeline.schemas import NovelParsed
from src.data.database import SessionLocal
from src.data.mongo import upsert_meta
from src.data.repository import upsert_canonical_novel, upsert_novel_source

"""
플랫폼 단위 크롤링 + 파싱 + 정규화 + DB 저장 파이프라인

- 개별 작품 처리: `_db_process`
- 병렬 처리: ThreadPoolExecutor
- KP / NS 플랫폼 별 동작 분기 처리
"""

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
    parser,
    remote_url:str ="") -> dict:
    """
    단일 작품 처리 워커

    처리 단계
    ----------
    1) HTML fetch
    2) HTML parsing
    3) 데이터 normalize
    4) Mongo 메타 upsert
    5) MySQL canonical novel upsert
    6) Novel Source upsert

    주의
    ----
    - 각 워커는 독립적인 SessionLocal() 사용
    - 실패 시 retry decorator 가 재시도 처리
    """
    t0 = perf_counter()
    session = SessionLocal()
    try:
        # ---------------- Fetch ----------------
        html = scraper.fetch_detail(p_no, remote_url)
        t_fetch = perf_counter()
        # ---------------- Parse ----------------
        data = parser.parse_detail(html)
        t_parse = perf_counter()
        del html

        try :
            # ---------------- Normalize + Schema Validation ----------------
            data['age_rating'] = map_age(data['age_rating'])
            data['completion_status'] = map_status(data['completion_status'])
            data['view_count'] = map_num(data['view_count'])
            data['episode_count'] = map_num(data['episode_count'])
            data['first_episode_date'] = map_date(data['first_episode_date'])

            obj = NovelParsed(**data) # 유효성 검사
        except Exception as e:
            # ex) 19세 이상 소설데이터는 검색 불가
            return {
                "p_no": p_no,
                "skipped": True,
                "fetch_ms": int((t_fetch - t0) * 1000),
                "parse_ms": int((t_parse - t_fetch) * 1000),
            }

        # ---------------- Mongo ----------------
        mongo_id = upsert_meta(
            title=obj.title,
            author_name=obj.author_name,
            description=obj.description,
            keywords=obj.keywords,
        )
        # ---------------- MySQL (novel) ----------------
        novel_id = upsert_canonical_novel(session, {
            "title": obj.title,
            "author_name": obj.author_name,
            "genre": obj.genre,
            "age_rating": obj.age_rating,
            "completion_status": obj.completion_status,
            "mongo_doc_id": mongo_id,
        })
        # ---------------- MySQL (novel source) ----------------
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

def kp_batch(remote_url:str, id_list:list[str],
             p_slug: str,scraper,parser):
    """
    KP 플랫폼 전용.
    - remote_url 별로 배치 처리 (Selenium shard 역할)
    """
    result = {}
    for p_no in id_list:
        result[p_no] = _db_process(p_no,p_slug, scraper, parser, remote_url)
    return result

def _run(
        p_slug: str,
        sc_fn_name: str,
        max_workers : int) -> dict:
    """
    플랫폼 단위 멀티쓰레드 실행 엔트리 포인트

    동작 흐름
    ----------
    1) scraper / parser 모듈 동적 로드
    2) 작품 ID 전체 수집
    3) ThreadPoolExecutor 로 병렬 처리
    4) KP / NS 플랫폼별 실행 전략 분기
    5) 결과 집계 및 요약 반환
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
        # -------- KP: Selenium Remote 분산 --------
        if p_slug == "KP" :
            num_remotes = min(4, max_workers)
            all_ids = list(all_ids)
            chunks = [all_ids[i::4] for i in range(4)]
            remotes = [
                        settings.SELENIUM_REMOTE_URL_1,
                        settings.SELENIUM_REMOTE_URL_2,
                        settings.SELENIUM_REMOTE_URL_3,
                        settings.SELENIUM_REMOTE_URL_4
                       ][:num_remotes]
            futs = [ex.submit(kp_batch, remote, chunk, p_slug, scraper, parser)
                    for remote, chunk in zip(remotes, chunks)]

            # 결과 병합 + 로깅
            for fut in as_completed(futs):
                try:
                    batch_results = fut.result()
                except Exception as e:
                    process_failed += 1
                    if len(errors) < 10:
                        errors.append({"url": f"{p_slug}/<batch>", "error": str(e)})
                    log.exception("[%s] batch worker crashed", p_slug)
                    continue

                for p_no, result in batch_results.items():
                    if result.get("skipped"):
                        skipped += 1
                        continue
                    if result.get("ok"):
                        process_ok += 1
                    else:
                        process_failed += 1
                        if len(errors) < 10:
                            errors.append({"url": f"{p_slug}/{p_no}", "error": result.get("error", "")})
                        log.warning("[%s] FAIL p_no=%s error=%s",
                                    p_slug, p_no, result.get("error", ""))
        # -------- NS: 단순 병렬 처리 --------
        elif p_slug == "NS" :
            futs = {
                ex.submit(_db_process, p_no, p_slug, scraper, parser): p_no
                for p_no in all_ids
            }
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
                else:
                    process_failed += 1
                    if len(errors) < 10:
                        errors.append({"url": f"{p_slug}/{p_no}", "error": result.get("error", "")})
                    log.warning(
                        "[%s] FAIL p_no=%s error=%s",p_slug,p_no,
                        result.get("error", ""),
                    )

    # ---------------- 결과 요약 ----------------
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
    """
    플랫폼 전체 초도 수집 실행
    """
    return _run( platform_slug, "fetch_all_pages_set",max_workers)
