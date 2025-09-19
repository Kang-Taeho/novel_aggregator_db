from datetime import datetime
from typing import Iterable
from src.scraping.base.browser import browser
from src.scraping.base.throttle import throttle

def fetch_all_pages_list() -> Iterable[str]:
    if False: yield ""

def fetch_top500_pages_list() -> Iterable[str]:
    if False: yield ""
    
def fetch_detail(url: str) -> str:
    with throttle(), browser() as drv:
        drv.get(url)
        return drv.page_source
