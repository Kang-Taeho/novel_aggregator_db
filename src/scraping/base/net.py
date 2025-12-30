import threading
import logging
import requests
from typing import Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

log = logging.getLogger(__name__)
log.propagate = True
log.setLevel(logging.INFO)

# 스레드별 독립적인 requests.Session 저장 공간
_THREAD_LOCAL = threading.local()

# 기본 HTTP 헤더 (일반 브라우저 유저에이전트와 유사)
_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 ... Chrome/114 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def _get_session(
    *,
    pool_size: int = 64,
    backoff_factor: float = 0.5,
    total_retries: int = 3,
    status_forcelist=(429, 500, 502, 503, 504),
) -> requests.Session:
    """
       스레드 로컬(thread-local)에 Session을 생성/재사용한다.
    """
    s = getattr(_THREAD_LOCAL, "session", None)
    if s:
        return s

    s = requests.Session()
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(
        pool_connections=pool_size,
        pool_maxsize=pool_size,
        max_retries=retry,
    )
    s.mount("https://", adapter)
    s.headers.update(_DEFAULT_HEADERS)
    _THREAD_LOCAL.session = s
    return s

def http_get(
    url: str,
    session: Optional[requests.Session] = None,
    timeout=(5, 15), # (connect, read)
    allow_redirects: bool = True,
) -> Optional[str]:
    """
        안정적인 HTTP GET 요청 수행함수.
        ----------
        - Session이 없으면 thread-local 세션 생성/재사용
        - Retry / 백오프는 Session 레벨에서 처리
        - 401 / 403 등 차단 응답 시 None 반환
        - 200~399 정상 응답만 body 반환
    """
    sess = session or _get_session()
    try:
        r = sess.get(
            url,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
    except requests.RequestException as e:
        log.warning("GET %s exception: %s", url, e)
        return None

    if r.status_code in (401, 403, 418, 451):
        log.warning("GET %s blocked with %s", url, r.status_code)
        return None

    if 200 <= r.status_code <= 399:
        return r.text

    log.warning("GET %s -> %s", url, r.status_code)
    return None
