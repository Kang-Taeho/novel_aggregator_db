from __future__ import annotations
from typing import Set
import logging, time, re, random
from src.scraping.base.browser import browser
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger(__name__)
RE_CONTENT_ID = re.compile(r"/content/(\d+)")
GENRE_URLS = [
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=86",   # 판타지
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=120",  # 현판
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=89",   # 로맨스
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=117",  # 로판
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=87",   # 무협
]

def _scroll_to_bottom(drv, min_jiggle_prob: float = 0.15, stable_ticks_needed: int = 5,
                      pause_sec: float = 1.2, max_seconds: int = 1800) -> None:
    """
    무한스크롤 페이지를 끝까지 로드:
    - 높이(scrollHeight)가 연속 stable_ticks_needed번 변하지 않으면 종료
    - 가상화 누락 방지로 간헐적 위아래 '지글' 스크롤
    - 최대 수행시간 안전장치 포함
    """
    t0 = time.time()
    last_h = 0
    stable = 0

    while True:
        # 맨 아래로
        drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_sec)

        # 필요 시 살짝 흔들기(가상화/관찰자 깨우기)
        if random.random() < min_jiggle_prob:
            try:
                drv.execute_script("window.scrollBy(0, -400);")
                time.sleep(0.2)
                drv.execute_script("window.scrollBy(0, 400);")
                time.sleep(0.2)
            except WebDriverException:
                pass

        h = drv.execute_script("return document.body.scrollHeight")
        if h == last_h:
            stable += 1
        else:
            stable = 0
            last_h = h

        if stable >= stable_ticks_needed:
            log.warning("scroll_to_bottom: %.1fs", time.time() - t0)
            break

        if time.time() - t0 > max_seconds:
            log.warning("scroll_to_bottom: timeout reached (%.1fs)", max_seconds)
            break

def fetch_all_pages_set() -> Set[str]:
    """
    1) 각 URL 로드 → 2) 끝까지 스크롤 → 3) JS로 series id 한 방에 추출 → 4) 전부 합집합 반환
    """
    found_all_ids: Set[str] = set()
    with browser() as drv:
        for url in GENRE_URLS:
            log.info("Loading: %s", url)
            drv.get(url)
            time.sleep(1.5)  # 초기 자바스크립트 부트 시간

            _scroll_to_bottom(drv)
            WebDriverWait(drv, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.cursor-pointer[href^='/content/']")
                )
            )

            html = drv.page_source
            ids = set(RE_CONTENT_ID.findall(html))
            log.info("Extracted %d ids from %s", len(ids), url)
            found_all_ids.update(ids)

    return found_all_ids

def fetch_detail(product_no: str) -> str:
    """상세 HTML 원문을 가져옵니다."""
    with browser() as drv:
        drv.get(f"https://page.kakao.com/content/{product_no}")
        return drv.page_source
