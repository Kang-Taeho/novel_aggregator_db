from typing import Iterable
from src.scraping.base.browser import browser
from src.scraping.base.throttle import throttle

SAMPLE_DETAIL_URL = [
    "https://page.kakao.com/content/67621678", #15세,UP,키워드
    "https://page.kakao.com/content/67672088", #신작,키워드
    "https://page.kakao.com/content/59137406", #키워드x
    "https://page.kakao.com/content/66943643", #단행본
]

def fetch_all_pages_list() -> Iterable[str]:
    if True: yield ""

def fetch_top500_pages_list() -> Iterable[str]:
    if False: yield ""

def fetch_detail(url: str) -> str:
    with throttle(), browser() as drv:
        drv.get(url)
        return drv.page_source
