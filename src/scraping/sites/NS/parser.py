from __future__ import annotations
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import re

def _text(el) -> Optional[str]:
    return el.get_text(" ", strip=True) if el else None

def parse_detail(html: str) -> Dict[str, Any]:
    """
    네이버시리즈 소설 상세 페이지에서 메타데이터를 파싱합니다.
    - keywords은 파싱 불가능
    - first_episode_date는 본문 DOM 의존도가 높아 기본 None 으로 둠 (필요 시 별도 API/리스트 페이지 파싱 권장)
    """
    data: Dict[str, Any] = {
        "title": None,
        "author_name": None,
        "platform_item_id": None,
        "genre": None,
        "age_rating": None,
        "description": None,
        "view_count": None,
        "first_episode_date": None, # 불가
        "completion_status": None,
        "keywords": None,           # 불가
        "episode_count": None,
    }
    # 19세 이상 로그인 시 정보열람 가능
    if "19세 미만의 청소년이 이용할 수 없습니다" in html : return data

    soup = BeautifulSoup(html, "lxml")
    # 작품 ID
    link = soup.find("link", rel="canonical")
    if link and link.get("href"):
        m = re.search(r"productNo=(\d+)", link["href"])
        if m:
            data["platform_item_id"] = m.group(1)

    content = soup.find("div", id="content")
    if content:
        head = content.find("div", class_="end_head")
        if head:
            # 제목
            h2 = head.find("h2")
            if h2:
                title = _text(h2) or ""
                data["title"] = title.replace("[독점]", "").strip() or None

            # 조회수
            vspan = head.select_one(".user_action_area .btn_download span")
            if vspan:
                data["view_count"] = _text(vspan)
            else :
                data["view_count"] = "0"

        # 장르/연재상태/작가/연령
        info_box = content.select_one("ul.end_info li.info_lst ul")
        if info_box:
            # 장르
            g = info_box.select_one("a[href*='genreCode']")
            if g:
                data["genre"] = _text(g)

            # 연재상태/작가/연령
            items = info_box.find_all("li")
            for i in range(len(items)):
                sp = items[i].find("span")
                label = sp.get_text(strip=True) if sp else ""
                # 연재상태
                if i == 0 and label:
                    data["completion_status"] = label
                # 작가
                if label == "글":
                    a = items[i].find("a")
                    data["author_name"] = _text(a)
                # 이용등급
                if len(items)-1 == i:
                    data["age_rating"] = _text(items[i])

    desc_blocks = soup.select("div.end_dsc ._synopsis")
    # 소개
    if desc_blocks:
        full = next((d for d in desc_blocks if "display: none" in (d.get("style") or "")), None)
        pick = full or desc_blocks[0]
        for a in pick.select("a.lk_more"):
            a.decompose()
        desc = _text(pick)
        if desc:
            data["description"] = desc.replace("\xa0", " ")

    # 총 회차
    tot = soup.select_one("h5.end_total_episode strong")
    if tot and (txt := _text(tot)):
        m = re.search(r"(\d+)", txt)
        if m:
            data["episode_count"] = m.group(1)

    return data
