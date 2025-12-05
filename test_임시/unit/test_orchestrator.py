import pytest
from src.pipeline import orchestrator
from src.data.database import SessionLocal
from src.data import models

def test_run_initial_full_handles_parse_error(monkeypatch):
    class FakeScraper:
        @staticmethod
        def fetch_all_pages_set():
            return ["ok1", "bad", "ok2"]

        @staticmethod
        def fetch_detail(p_no: str) -> str:
            return f"<html>{p_no}</html>"

    class FakeParser:
        @staticmethod
        def parse_detail(html: str) -> dict:
            if "bad" in html:
                raise ValueError("parse error")
            import re
            m = re.search(r"(ok\d)", html)
            p_no = m.group(1)
            return {
                "platform_item_id": p_no,
                "title": f"Title {p_no}",
                "author_name": "Tester",
                "genre": "테스트",
                "age_rating": "ALL",
                "completion_status": "ongoing",
                "view_count": "0",
                "episode_count": "0",
                "first_episode_date": None,
                "description": "",
                "keywords": [],
            }

    def fake_import_module(path: str):
        if path.endswith(".scraper"):
            return FakeScraper
        if path.endswith(".parser"):
            return FakeParser
        raise ImportError(path)

    monkeypatch.setattr(orchestrator, "import_module", fake_import_module)

    result = orchestrator.run_initial_full(platform_slug="KP", max_workers=3)

    assert result["total"] == 3
    assert result["success"] == 2
    assert result["failed"] == 1
    assert len(result["errors_sample"]) >= 1

    with SessionLocal() as db:
        db.query(models.NovelSource).delete()
        db.query(models.Novel).delete()
        db.commit()