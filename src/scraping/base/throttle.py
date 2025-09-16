import time, random
from contextlib import contextmanager
from src.core.config import settings

@contextmanager
def throttle():
    try: yield
    finally: time.sleep((settings.REQUEST_MIN_INTERVAL_MS + random.randint(0,200))/1000.0)
