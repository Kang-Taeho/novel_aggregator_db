from __future__ import annotations
import logging, sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import health, jobs
from src.apps.scheduler.main import start_scheduler, shutdown_scheduler

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)  # <- INFO 이하 출력 허용
    h = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    h.setFormatter(fmt)
    root.handlers = [h]

    # 서브 로거 레벨도 명시(선택)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    logging.getLogger("selenium").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
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
