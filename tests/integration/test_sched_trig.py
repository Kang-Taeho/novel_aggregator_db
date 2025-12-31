
import pytest
from fastapi.testclient import TestClient
from src.data.database import SessionLocal
from src.data import models
# FastAPI 앱(실제 main.py) 임포트
from src.apps.api.main import app


@pytest.fixture(autouse=True)
def _env_interval(monkeypatch):
    monkeypatch.setenv("SCHED_TEST_INTERVAL_HOUR", "4")
    yield

@pytest.fixture
def client():
    # startup/shutdown 훅을 포함해 앱을 띄움 → 스케줄러 시작
    with TestClient(app) as c:
        yield c


def test_scheduler_triggers(monkeypatch):
    from src.apps.scheduler.jobs import do_initial
    def fake_run(**kw):

        return {"total":1,"success":1,"failed":0,"skipped":0,"duration_ms":10,"errors_sample":[]}

    # orchestrator 함수 대체
    monkeypatch.setattr("src.apps.scheduler.jobs.run_pipeline", lambda **k: fake_run(**k))

    jr = do_initial(platform_slug="test", max_workers=2, test_bool=True)
    assert jr is not None
    assert jr["status"] == "SUCCEEDED"

    with (SessionLocal() as db):
        db.query(models.JobRun
                 ).filter(models.JobRun.platform == "test").delete()
        db.commit()
