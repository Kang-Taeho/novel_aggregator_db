from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.dialects.mysql import insert as mysql_insert

from src.core.config import settings
from src.data.models import JobRun
from src.data.database import SessionLocal
from src.pipeline.orchestrator import run_initial_full as run_pipeline

def _today_key(job_type: str, platform_slug: str) -> str:
    """
    오늘 날짜/시간 기준으로 유니크한 job_key 생성.

    형식 예:
        initial_full:KP:20251230-134501
        test_initial_full:NS:20251230-090001
    """

    kst = ZoneInfo(settings.TZ)
    d = datetime.now(kst).strftime("%Y%m%d-%H%M%S")
    return  f"{job_type}:{platform_slug}:{d}"

def do_initial(platform_slug: str, max_workers: int, test_bool:bool=False) -> dict:
    """
       플랫폼별 초기 전체 수집 잡 실행 + JobRun 기록.

       흐름
       ----
       1) JobRun 메타데이터 구성 (RUNNING 상태로 시작)
       2) run_pipeline() 호출하여 실제 크롤링/파이프라인 실행
       3) 결과 통계를 JobRun.metrics_json / error_sample_json 에 저장
       4) JobRun 테이블에 insert (로그성 기록용)
       5) 최종적으로 jr(dict)를 반환
       """
    session = SessionLocal()
    # 테스트/운영 구분에 따라 job_type만 다르게 기록
    if test_bool: job_key = _today_key("test_initial_full", platform_slug)
    else : job_key = _today_key("initial_full", platform_slug)

    # JobRun 초기 상태 정보
    jr = {
        "job_key" : job_key,
        "platform" : platform_slug,
        "mode" : "initial_full",
        "started_at" : datetime.now(ZoneInfo(settings.TZ)),
        "status" : "RUNNING"
    }
    try:
        # 실제 파이프라인 실행
        result = run_pipeline(platform_slug=platform_slug, max_workers=max_workers)

        # 에러 샘플 및 메트릭 정리
        jr["error_sample_json"] = result.get("errors_sample", [])
        jr["metrics_json"] = {
            "total": result.get("total", 0),
            "success": result.get("success", 0),
            "failed": result.get("failed", 0),
            "skipped": result.get("skipped", 0),
            "duration_ms": result.get("duration_ms", 0),
        }
        jr["status"] = "SUCCEEDED"
        jr["finished_at"] = datetime.now(ZoneInfo(settings.TZ))

    except Exception:
        jr["status"] = "FAILED"

    try :
        # JobRun 테이블에 로그성 데이터 insert
        stmt = mysql_insert(JobRun).values(
            job_key=jr.get("job_key"),
            platform=jr.get("platform"),
            mode=jr.get("mode"),
            started_at=jr.get("started_at"),
            finished_at=jr.get("finished_at"),
            status=jr.get("status"),
            metrics_json=jr.get("metrics_json"),
            error_sample_json=jr.get("error_sample_json"),
        )
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
        return jr