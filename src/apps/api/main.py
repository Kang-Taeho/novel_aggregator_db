from __future__ import annotations
import logging, sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import health, jobs
from src.apps.scheduler.main import start_scheduler, shutdown_scheduler

def setup_logging():
    """
    애플리케이션 공용 로깅 설정

    - root logger 기준으로 INFO 레벨 이상 출력\
    - 간결한 포맷 적용 (시간 / 레벨 / 로거명 / 메시지)
    - 하위 라이브러리 로거 레벨 명시 설정
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)  # <- INFO 이하 출력 허용
    h = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    h.setFormatter(fmt)
    root.handlers = [h]

    # 서브 로거 레벨 명시
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    logging.getLogger("selenium").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션 lifecycle

    애플리케이션 시작 시:
        - 로깅 초기화
        - 스케줄러 시작

    애플리케이션 종료 시:
        - 스케줄러 안전 종료
    """
    setup_logging()
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()

setup_logging()
app = FastAPI(title="Novel Aggregator API", version="0.1.0", lifespan=lifespan)
app.include_router(health.router)
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
