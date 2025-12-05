# tests/unit/test_schemas.py
from pydantic import ValidationError
from src.pipeline.schemas import NovelParsed

def test_parsed_schema_ok():
    NovelParsed(platform_item_id="123", title="T", author_name="A")

def test_parsed_schema_fail_no_id():
    import pytest
    with pytest.raises(ValidationError):
        NovelParsed(platform_item_id="", title="T")



