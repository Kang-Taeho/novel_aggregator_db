from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.dialects.mysql import insert as mysql_insert

from src.core.config import settings
from src.data.models import JobRun
from src.data.database import SessionLocal
from src.pipeline.orchestrator import run_initial_full as run_pipeline

def _today_key(job_type: str, platform_slug: str) -> str:
    kst = ZoneInfo(settings.TZ)
    d = datetime.now(kst).strftime("%Y%m%d-%H%M%S")
    return  f"{job_type}:{platform_slug}:{d}"

def do_initial(platform_slug: str, max_workers: int) -> None:
    session = SessionLocal()
    job_key = _today_key("initial_full", platform_slug)
    jr = {
        "job_key" : job_key,
        "platform" : platform_slug,
        "mode" : "initial_full",
        "started_at" : datetime.now(ZoneInfo(settings.TZ)),
        "status" : "RUNNING"
    }
    try:
        result = run_pipeline(platform_slug=platform_slug, max_workers=max_workers)

        jr["error_sample_json"] = result.get("errors_sample", [])
        jr["metrics_json"] = {
            "total": result.get("total", 0),
            "success": result.get("success", 0),
            "failed": result.get("failed", 0),
            "skipped": result.get("skipped", 0),
            "duration_ms": result.get("duration_ms", 0),
        }
        jr["status"] = "SUCCESSED"
        jr["finished_at"] = datetime.now(ZoneInfo(settings.TZ))

    except Exception:
        jr["status"] = "FAILED"

    try :
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