# tests/e2e/test_jobs_api_e2e.py
from fastapi.testclient import TestClient
from src.apps.api.main import app
from src.core import config

def test_jobs_api_json_success(monkeypatch):
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_HOURS", "0")
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_SECONDS", "30")

    def fake_run(platform_slug: str, max_workers: int):
        return {"total": 2, "success": 2, "failed": 0, "skipped": 0, "duration_ms": 20, "errors_sample": []}
    monkeypatch.setattr("src.apps.api.routers.jobs.run_pipeline", fake_run)

    with TestClient(app) as c:
        r = c.post("/jobs/scrape?platform_slug=KP")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] == 2
        assert body["failed"] == 0

def test_jobs_api_json_failure(monkeypatch):
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_HOURS", "0")
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_SECONDS", "30")

    def fail(*a, **k):
        raise RuntimeError("boom!")
    monkeypatch.setattr("src.apps.api.routers.jobs.run_pipeline", fail)

    with TestClient(app) as c:
        r = c.post("/jobs/scrape?platform_slug=KP")
        assert r.status_code == 500
        body = r.json()
        assert "error" in body
        assert body.get("platform_slug") == "KP"
