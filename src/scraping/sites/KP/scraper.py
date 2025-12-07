from __future__ import annotations
from typing import Set
import logging, time, re, random
from src.scraping.base.browser import browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)

RE_CONTENT_ID = re.compile(r"/content/(\d+)")
GENRE_URLS = [
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=86",   # 판타지
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=120",  # 현판
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=89",   # 로맨스
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=117",  # 로판
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=87",   # 무협
]

def _scroll_to_bottom(
        drv,
        min_jiggle_prob: float = 0.07,
        stable_ticks_needed: int = 2,
        pause_sec: float = 0.3,
        max_seconds: int = 4800) -> None:
    """
    무한스크롤 페이지를 끝까지 로드:
    - 높이(scrollHeight)가 연속 stable_ticks_needed번 변하지 않으면 종료
    - 가상화 누락 방지로 간헐적 위아래 '지글' 스크롤
    - 최대 수행시간 안전장치 포함
    """
    t0 = time.time()
    ten_min = 600
    last_h = 0
    stable = 0

    while True:
        drv.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        if time.time() - t0 > ten_min:
            pause_sec += 0.05
            ten_min += 600
        time.sleep(pause_sec)

        # 필요 시 살짝 흔들기(가상화/관찰자 깨우기)
        if stable >= 1 and random.random() < min_jiggle_prob:
            try:
                drv.execute_script("window.scrollBy(0, -400);")
                time.sleep(0.1)
                drv.execute_script("window.scrollBy(0, 400);")
                time.sleep(0.1)
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
    1) 각 URL 로드 → 2) 끝까지 스크롤 → 3) series id 한 방에 추출 → 4) 전부 합집합 반환
    """
    found_all_ids: Set[str] = set()
    for url in GENRE_URLS:
        log.info("Loading: %s", url)
        with browser() as drv:
            drv.get(url)
            WebDriverWait(drv, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.cursor-pointer[href^='/content/']")
                )
            )
            _scroll_to_bottom(drv)
            time.sleep(5) # 스크롤 최종 마무리 시간

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
