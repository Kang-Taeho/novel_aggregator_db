from __future__ import annotations
import random, time, functools, logging
from typing import Iterable, Type

log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)

def _sleep_with_backoff(attempt: int, base: float, cap: float, jitter: float) -> None:
    back = min(cap, base * (2 ** attempt))
    time.sleep(back + random.uniform(0.0, jitter))

def retry(
    *,
    exceptions: Iterable[Type[BaseException]] = (Exception,),
    tries: int = 3,
    base: float = 1.0,
    cap: float = 8.0,
    jitter: float = 0.3,
):
    """
    예: @retry(exceptions=(TimeoutError,), tries=3, base=1, cap=8, jitter=0.3)
    - 지수 백오프(1,2,4,8.. cap) + 지터
    - 예외가 exceptions에 해당할 때만 재시도
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(tries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == tries - 1:
                        raise
                    log.warning("retry #%d for %s: %s", attempt + 1, fn.__name__, e)
                    _sleep_with_backoff(attempt, base, cap, jitter)
            raise last_exc
        return wrapper
    return deco
