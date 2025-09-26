from typing import Iterable
import requests


def fetch_all_pages_list() -> Iterable[str]:
    if False: yield ""


def fetch_top500_pages_list() -> Iterable[str]:
    if False: yield ""


def fetch_detail(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 ... Chrome/114 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    return requests.get(url, headers=headers).text
