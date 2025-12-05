# tests/unit/test_retry.py
from src.core.retry import retry

def test_retry_attempts():
    calls = {"n": 0}

    @retry(tries=3, base=0.0, cap=0.0, jitter=0.0)
    def flaky():
        calls["n"] += 1
        raise ValueError("boom")

    import pytest
    with pytest.raises(ValueError):
        flaky()
    assert calls["n"] == 3
