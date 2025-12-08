from typing import Set
from urllib.parse import urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor, as_completed
import re, logging, math
from src.scraping.base.net import http_get

log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)

_PER_PAGE = 25  # 한 페이지당 25개
_MAX_WORKERS = 8 # 테스트 결과로 조정
GENRE_BASE = "https://series.naver.com/novel/categoryProductList.series"
GENRE_CODES = ["201","207","202","208","206","203","205"]
            #로맨스    로판  판타지 현판  무협  미스테리    라이트노벨
RE_PRODUCT_HREF = re.compile(r"productNo=(\d+)")

def _build_url(c: str, page: int) -> str:
    qs = {
        "categoryTypeCode": "genre",
        "genreCode": c,
        "page": str(page)
    }
    return f"{GENRE_BASE}?{urlencode(qs)}"

def _total_pages(c) -> int:
    html = http_get(_build_url(c,1))
    if not html:
        return 1
    soup = BeautifulSoup(html, "lxml")
    total_div = soup.find("div", class_="total")
    if not total_div:
        return 1
    txt = total_div.get_text(strip=True)
    total_cnt = int("".join(ch for ch in txt if ch.isdigit() or ch == ",").replace(",", "") or 0)

    return max(1, math.ceil(total_cnt / _PER_PAGE))

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
def _fetch_page_ids(c,page: int) -> Set[str]:
    url = _build_url(c,page)
    html = http_get(url)
    if not html:
        log.warning("failed to fetch page=%s", page)
        return set()
    return  _parse_product_ids_bs4(html)


def fetch_all_pages_set() -> Set[str]:
    found_all_ids: Set[str] = set()

    for c in GENRE_CODES :
        end_page = _total_pages(c)
        log.info("Loading: genre_code(%s)", c)
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
            futs = {ex.submit(_fetch_page_ids,c, p): p for p in range(1, end_page + 1)}
            for fut in as_completed(futs):
                p = futs[fut]
                try:
                    ids = fut.result()
                    found_all_ids.update(ids)
                except Exception as e:
                    log.warning("page %s failed: %s", p, e)
        log.info("Extracted %d ids from GENRE_CODE(%s)", len(found_all_ids), c)
    return found_all_ids


def fetch_detail(product_no: str, remote_url: str) -> str:
    return http_get(f"https://series.naver.com/novel/detail.series?productNo={product_no}")
