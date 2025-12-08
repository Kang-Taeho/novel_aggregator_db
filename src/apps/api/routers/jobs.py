from __future__ import annotations
from pydantic import BaseModel
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.pipeline.orchestrator import run_initial_full as run_pipeline
from src.core.config import settings

router = APIRouter()

class JobErrorSample(BaseModel):
    url: str
    error: str

class ScrapeJobResponse(BaseModel):
    platform_slug: str
    sc_fn: str
    total: int
    success: int
    failed: int
    skipped: int
    duration_ms: int
    errors_sample: list[JobErrorSample] = []

@router.post("/scrape")
def scrape_job(
    platform_slug: str = Query(..., description="플랫폼 코드, 예: KP, NS")
):
    if platform_slug == "KP": max_workers = int(settings.SCHED_MAX_WORKERS_KP)
    elif platform_slug == "NS": max_workers = int(settings.SCHED_MAX_WORKERS_NS)
    else : max_workers = 8

    try:
        result = run_pipeline(platform_slug=platform_slug, max_workers=max_workers)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "platform_slug": platform_slug,
                "sc_fn": "run_initial_full",
                "error": str(e),
            },
        )
