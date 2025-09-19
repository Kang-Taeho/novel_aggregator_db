from __future__ import annotations
from fastapi import FastAPI
from .routers import health, jobs
app = FastAPI(title="Novel Aggregator API", version="0.1.0")
app.include_router(health.router)
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
