from typing import Set
from urllib.parse import urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor, as_completed
import re, logging, math
from src.scraping.base.net import http_get

log = logging.getLogger(__name__)

_PER_PAGE = 25  # 한 페이지당 25개로 고정
_MAX_WORKERS = 32 # 멀티스레드 테스트 후 결정
BASE_URL = "https://series.naver.com/novel/categoryProductList.series"
RE_PRODUCT_HREF = re.compile(r"productNo=(\d+)")

def _total_pages_25() -> int:
    params = {
        "categoryTypeCode": "series",
        "page": "1",
    }
    html = http_get(BASE_URL, params)
    if not html:
        return 1
    soup = BeautifulSoup(html, "lxml")
    total_div = soup.find("div", class_="total")
    if not total_div:
        return 1
    txt = total_div.get_text(strip=True)
    total_cnt = int("".join(ch for ch in txt if ch.isdigit() or ch == ",").replace(",", "") or 0)

    return max(1, math.ceil(total_cnt / _PER_PAGE))

def _build_url(page: int) -> str:
    # 원본 쿼리: categoryTypeCode=series&page=1
    qs = {
        "categoryTypeCode": "series",
        "page": str(page),
    }
    return f"{BASE_URL}?{urlencode(qs)}"

def _parse_product_ids_bs4(html: str) -> Set[str]:
    """
    ul.lst_list 안쪽만 부분 파싱해서 a[href*='productNo=']에서 productNo만 추출.
    """
    found_ids: Set[str] = set()

    only_list = SoupStrainer("ul", {"class": "lst_list"})
    soup = BeautifulSoup(html, "lxml", parse_only=only_list)

    if not soup:
        return found_ids

    # 2) 앵커의 href에서 productNo 뽑기
    for a in soup.select('li a[href*="productNo="]'):
        href = a.get("href", "")
        m = RE_PRODUCT_HREF.search(href)
        if m:
            found_ids.add(m.group(1))
            continue
        # 보수적 경로: URL 파싱 후 query에서 추출
        q = parse_qs(urlparse(href).query)
        if "productNo" in q and q["productNo"]:
            try:
                found_ids.add(q["productNo"][0])
            except ValueError:
                pass
    return found_ids

# =========================
# 페이지 단위 수집
# =========================
def _fetch_page_ids(page: int) -> Set[str]:
    url = _build_url(page)
    html = http_get(url)
    if not html:
        log.warning("failed to fetch page=%s", page)
        return set()
    return  _parse_product_ids_bs4(html)


def fetch_all_pages_set() -> Set[str]:
    found_all_ids: Set[str] = set()
    end_page = _total_pages_25()

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
        futs = {ex.submit(_fetch_page_ids, p): p for p in range(1, end_page + 1)}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                ids = fut.result()
                found_all_ids.update(ids)
            except Exception as e:
                log.warning("page %s failed: %s", p, e)
    return found_all_ids


def fetch_detail(product_no: str) -> str:
    return http_get(f"https://series.naver.com/novel/detail.series?productNo={product_no}")
