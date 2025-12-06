# tests/integration/test_jobs_integration.py
from sqlalchemy import text
from src.core import config
from src.apps.scheduler.jobs import do_initial
from src.data.database import SessionLocal

def test_do_daily_success(monkeypatch):
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_HOURS", "0")
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_SECONDS", "2")

    def fake_run_initial_full(platform_slug,max_workers):
        return {"platform_slug":platform_slug,"total":5,"success":5,"failed":0,"skipped":0,"duration_ms":111,"errors_sample":[]}
    monkeypatch.setattr("src.apps.scheduler.jobs.run_pipeline", fake_run_initial_full)

    do_initial(platform_slug="KP", max_workers=2, test_bool=True)

    s=SessionLocal()
    try:
        row=s.execute(text("SELECT status, metrics_json FROM job_runs WHERE mode='initial_full'")).mappings().first()
        assert row and row["status"]=="SUCCEEDED"
        # 테스트 기록 지우기
        s.execute(text("DELETE FROM job_runs WHERE job_key LIKE 'test%'"))
        s.commit()
    finally:
        s.close()
