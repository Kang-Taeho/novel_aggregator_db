from __future__ import annotations
import json
from typing import Any, Dict
from bs4 import BeautifulSoup


def _get(d: dict, *path, default=None):
    """중첩 딕셔너리 안전 접근: _get(obj, 'a','b','c', default=None)"""
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur

def parse_detail(html: str) -> Dict[str, Any]:
    """
    KakaoPage 상세 페이지 HTML에서 __NEXT_DATA__ 기반으로 메타데이터 추출.
    - 안정적으로 제공되는 필드만 채움
    - episode_count는 본문 DOM 의존도가 높아 기본 None 으로 둠 (필요 시 별도 API/리스트 페이지 파싱 권장)
    - keywords는 별도의 페이지이므로 시간이 너무 걸려 생략
    """
    data: Dict[str, Any] = {
        "title": None,
        "author_name": None,
        "platform_item_id": None,
        "genre": None,
        "age_rating": None,
        "description": None,
        "view_count": None,
        "first_episode_date": None,
        "completion_status": None,
        # "keywords": None,
        # "episode_count": None,
    }
    # 19세 이상 로그인 시 정보열람 가능
    if "서비스 이용을 위해 연령 확인이 필요 합니다" in html : return data

    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", id="__NEXT_DATA__")
    if not (script and script.string):
        return data

    try:
        nxt = json.loads(script.string)
        props = _get(nxt, "props", "pageProps", "initialProps", default={})
        meta = _get(props, "metaInfo", default={})
        dq = _get(props, "dehydratedState", "queries", default=[]) or []

        content = {}
        if dq and isinstance(dq[0], dict):
            content = _get(
                dq[0], "state", "data", "contentHomeOverview", "content", default={}
            ) or {}

        # 기본 메타
        data["platform_item_id"] = content.get("seriesId") or props.get("seriesId")
        data["title"] = content.get("title") or meta.get("ogTitle") or meta.get("title")
        data["author_name"] = content.get("authors") or meta.get("author")
        data["description"] = content.get("description") or meta.get("description")

        # 장르/등급
        data["genre"] = content.get("subcategory") or content.get("category")
        data["age_rating"] = content.get("ageGrade")

        # 날짜(문자열 그대로 보관)
        data["first_episode_date"] = content.get("startSaleDt")

        # 연재 상태
        data["completion_status"] = content.get("onIssue")

        # 조회수
        svc = content.get("serviceProperty") or {}
        vc = svc.get("viewCount")
        if isinstance(vc, (int, float)):
            data["view_count"] = int(vc)

    except Exception:
        # 구조 변화/키 누락 시 조용히 폴백 (상위에서 재시도/로그)
        pass

    return data
