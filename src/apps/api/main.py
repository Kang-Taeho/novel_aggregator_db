from __future__ import annotations
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import health, jobs
from src.apps.scheduler.main import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()

app = FastAPI(title="Novel Aggregator API", version="0.1.0", lifespan="lifespan")
app.include_router(health.router)
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
