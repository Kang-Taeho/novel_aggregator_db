from __future__ import annotations
from pydantic import BaseModel
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.pipeline.orchestrator import run_initial_full as run_pipeline
from src.core.config import settings

router = APIRouter()

class JobErrorSample(BaseModel):
    """
    실패한 작업 중 일부 샘플 정보를 담는 모델
    """
    url: str
    error: str

class ScrapeJobResponse(BaseModel):
    """
    스크래핑 배치 작업 실행 결과 응답 모델
    """
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
    """
    플랫폼 전체 대상 초기 스크래핑 실행 API

    - platform_slug 에 따라 파이프라인 실행
    - KP / NS 는 설정값 기반으로 worker 수를 다르게 적용
    - run_pipeline (orchestrator) 실행
    - 성공 시 정리된 통계 결과 반환
    - 실패 시 HTTP 500 + 에러 내용 반환
    """
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
