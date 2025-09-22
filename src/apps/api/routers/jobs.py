from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from src.data.database import SessionLocal
from src.pipeline.orchestrator import (run_initial_full as run_pipeline_initial,
                                       run_daily_top500 as run_pipeline_daily)

router = APIRouter()

class ScrapeBody(BaseModel):
    platform: str
    mode: str = "full | daily-500"

@router.post("/scrape")
def scrape(body: ScrapeBody):
    with SessionLocal() as session:
        if body.mode == "full" :
            res = run_pipeline_initial(session, platform=body.platform)
        elif body.mode == "daily" :
            res = run_pipeline_daily(session, platform=body.platform)
        else :
            return {"status": "error", "result": "Unknown mode"}
        return {"mode": body.mode, "status": "ok", "result": res}
# res  = {
#         "platform": platform,
#         "list_fn": list_fn_name,
#         "total": process_total,
#         "success": process_ok,
#         "failed": process_failed,
#         "errors_sample": errors,
#         "duration_ms": int((perf_counter() - t_start) * 1000),
#     }