from bs4 import BeautifulSoup
import json

# parsing 목록
# title, author_name, platform_item_id, genre
# description, view_count, first_episode_date
# age_rating, completion_status
# 비효율 가능: episode_count
# 비효율 불가: keywords

def _text(m):
    if m: return m.get("content")
    else : return None

def parse_detail(html: str) -> dict:
    #overview page
    soup = BeautifulSoup(html, "lxml")
    data = dict()
    script = soup.find("script", id="__NEXT_DATA__")
    if script and script.string:
        try:
            nxt = json.loads(script.string)
            props = nxt.get("props", {}).get("pageProps", {}).get("initialProps", {})
            meta = props.get("metaInfo", {})
            dq = props.get("dehydratedState", {}).get("queries", []) or []
            content = {}
            if dq and isinstance(dq[0], dict):
                content = (dq[0].get("state", {})
                           .get("data", {})
                           .get("contentHomeOverview", {})
                           .get("content", {})) or {}

            data["platform_item_id"] = content.get("seriesId") or props.get("seriesId")
            data["title"] = content.get("title") or meta.get("title")
            data["author_name"] = content.get("authors") or meta.get("author")
            data["description"] = content.get("description") or meta.get("description")
            data["genre"] = content.get("subcategory")
            data["age_rating"] = content.get("ageGrade")
            data["first_episode_date"] =  content.get("startSaleDt")
            data["completion_status"] = content.get("onIssue")
            data["view_count"] = content.get("serviceProperty").get("viewCount")
            data["episode_count"] = (soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr '
                                                     '> div.flex.h-full.flex-1.flex-col > div '
                                                     '> div.flex.flex-col.overflow-hidden.mb-28pxr.ml-4px.w-632pxr.rounded-12pxr '
                                                     '> div.flex-1.flex.flex-col > div.rounded-b-12pxr.bg-bg-a-20 '
                                                     '> div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-20.px-18pxr '
                                                     '> div.flex.h-full.flex-1.items-center.space-x-8pxr > span')
                                     .get_text(strip=True).replace("전체 ", ""))
        except (KeyError, ValueError, TypeError) :
            pass

    return data