from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from src.data.database import SessionLocal
from src.pipeline.orchestrator import run_initial_full as run_pipeline

router = APIRouter()

class ScrapeBody(BaseModel):
    platform: str

@router.post("/scrape")
def scrape(body: ScrapeBody):
    with SessionLocal() as session:
        res = run_pipeline(platform=body.platform)
        return {"status": "ok", "result": res}
# res  = {
#         "platform": platform,
#         "list_fn": list_fn_name,
#         "total": process_total,
#         "success": process_ok,
#         "failed": process_failed,
#         "errors_sample": errors,
#         "duration_ms": int((perf_counter() - t_start) * 1000),
#     }