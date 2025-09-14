from __future__ import annotations
from fastapi import FastAPI
from .test_routers import health, jobs
app = FastAPI(title="Novel Aggregator API", version="0.3.0")
app.include_router(health.router)
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])