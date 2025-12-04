def test_scheduler_triggers(monkeypatch):
    from src.apps.scheduler.jobs import do_initial
    calls = []
    def fake_run(**kw):
        calls.append(kw); return {"total":1,"success":1,"failed":0,"skipped":0,"duration_ms":10,"errors_sample":[]}
    # orchestrator 함수 대체
    monkeypatch.setattr("src.apps.scheduler.jobs.run_pipeline", lambda **k: fake_run(**k))
    # 직접 호출
    do_initial(platform_slug="KP", max_workers=2)
    assert len(calls) == 1
