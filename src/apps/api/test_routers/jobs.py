from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from src.data.database import SessionLocal
from src.pipeline.orchestrator import run as run_pipeline

router = APIRouter()

class ScrapeBody(BaseModel):
    platform: str
    scope: str = "incremental"
    since: datetime | None = None

@router.post("/scrape")
def scrape(body: ScrapeBody):
    with SessionLocal() as session:
        res = run_pipeline(session, platform=body.platform, scope=body.scope, since=body.since)
        return {"status": "ok", "result": res}
