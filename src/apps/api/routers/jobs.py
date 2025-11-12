from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.pipeline.orchestrator import run_initial_full as run_pipeline

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

@router.post("/scrape", response_model=ScrapeJobResponse)
def scrape_job(
    platform_slug: str = Query(..., description="플랫폼 코드, 예: KP, NS"),
    max_workers: int = Query(12, ge=1, le=64),
):
    result = run_pipeline(platform_slug=platform_slug, max_workers=max_workers)
    return result
