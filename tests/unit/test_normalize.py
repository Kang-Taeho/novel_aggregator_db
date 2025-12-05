# tests/unit/test_normalize.py
from src.pipeline.normalize import map_age, map_status, map_num, map_date
from datetime import date

def test_map_age():
    assert map_age("Fifteen") == "15"
    assert map_age("15세 이용가") == "15"
    assert map_age("전체 이용가") == "ALL"

def test_map_status():
    assert map_status("completed") == "completed"
    assert map_status("완결") == "completed"
    assert map_status("Ing") == "ongoing"

def test_map_num():
    assert map_num("1.2만") == 12000
    assert map_num("1,234") == 1245
    assert map_num("0") == 0

def test_map_date():
    assert isinstance(map_date('2021-11-17T02:52:26.000Z'),date)
    assert map_date('2021-11-17T02:52:26.000Z') == "2021-11-17"
    assert map_date(None) == None

