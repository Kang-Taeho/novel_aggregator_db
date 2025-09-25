from bs4 import BeautifulSoup
import re


def parse_detail(html: str) -> dict:
    """문피아 소설 상세 페이지에서 메타데이터를 파싱합니다."""

    soup = BeautifulSoup(html, "lxml")
    data = {
        "title": None,
        "author_name": None,
        "platform_item_id": None,
        "genre": None,
        "description": None,
        "view_count": None,
        "first_episode_date": None,
        "completion_status": None,
        "keywords": None,
        "episode_count": None,
    }

    # ======================
    # 1. detail-box 영역
    # ======================
    detail = soup.find("div", class_="dd detail-box")
    if detail:
        try:
            # 작품 ID
            a_tag = detail.select_one("div.title-wrap a")
            if a_tag:
                href = a_tag.get("href", "")
                match = re.search(r"/(\d+)", href)
                if match:
                    data["platform_item_id"] = match.group(1)

                data["title"] = a_tag.get("title") or a_tag.get_text(strip=True)

            # 장르
            genre = detail.select_one("p.meta-path strong")
            if genre:
                data["genre"] = genre.get_text(strip=True)

            # 작가
            author = detail.select_one("dl.meta-author strong")
            if author:
                data["author_name"] = author.get_text(strip=True)

            # 연재 여부
            if detail.find("div", class_="novel-period"):
                data["completion_status"] = "연재"
            else:
                data["completion_status"] = "완결"

            # 등록일 / 회차 / 조회수
            meta_blocks = detail.select("dl.meta-etc.meta")
            if meta_blocks:
                # 첫 블록 → 등록일
                first_date = meta_blocks[0].find("dd")
                if first_date:
                    data["first_episode_date"] = first_date.get_text(strip=True)

                # 두 번째 블록 → 회차, 조회수
                if len(meta_blocks) > 1:
                    stats = meta_blocks[1].find_all("dd")
                    if len(stats) >= 1:
                        data["episode_count"] = (
                            stats[0].get_text(strip=True).replace(" 회", "")
                        )
                    if len(stats) >= 2:
                        data["view_count"] = stats[1].get_text(strip=True)

        except Exception:
            pass

    # ======================
    # 2. STORY-BOX 영역
    # ======================
    story_box = soup.find("div", id="STORY-BOX")
    if story_box:
        try:
            # 작품소개
            desc = story_box.find("p", class_="story")
            if desc:
                data["description"] = desc.get_text(strip=True)

            # 키워드
            keywords = story_box.select("div.tag-list a")
            if keywords:
                data["keywords"] = [k.get_text(strip=True) for k in keywords]

        except Exception:
            pass

    return data
