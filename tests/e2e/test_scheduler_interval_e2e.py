# tests/e2e/test_scheduler_interval_e2e.py
import time, json
from fastapi.testclient import TestClient
from sqlalchemy import text
from src.core import config

from src.apps.api.main import app
from src.data.database import SessionLocal

"""
APScheduler Interval 기반 자동 실행 E2E 테스트

검증 목표
---------
1) scheduler 가 interval trigger 로 실제 job 을 실행하는지 확인
2) job_runs 테이블에 기록이 생성되는지 확인
3) status = SUCCEEDED 인지 확인
4) metrics_json 값까지 정상 저장되는지 확인
"""

def test_interval_triggers_job(monkeypatch):
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_HOURS", "0")
    monkeypatch.setattr(config.settings,"SCHED_TEST_INTERVAL_SECONDS", "2")

    def fake_run(platform_slug: str, max_workers: int):
        return {"total": 1, "success": 1, "failed": 0, "skipped": 0, "duration_ms": 10, "errors_sample": []}
    monkeypatch.setattr("src.apps.scheduler.jobs.run_pipeline", fake_run)

    with (TestClient(app)):
        time.sleep(5)  # 2~3회 실행 기회
        s = SessionLocal()
        try:
            row = s.execute(text("SELECT status, metrics_json FROM job_runs ORDER BY id DESC LIMIT 1")
                            ).mappings().first()
            assert row is not None
            assert row["status"] == "SUCCEEDED"
            m = json.loads(row["metrics_json"])
            assert m["total"] == 1
            #테스트 기록 지우기
            s.execute(text("DELETE FROM job_runs WHERE job_key LIKE 'test%'"))
            s.commit()
        finally:
            s.close()
