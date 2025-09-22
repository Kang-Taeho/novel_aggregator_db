from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver

# parsing 목록
# title, author_name, platform_item_id, episode_count, first_episode_date, view_count
# description, keywords
# age_rating, completion_status

def parse_detail(html: str) -> dict:
    data = dict()

    driver = webdriver.Chrome()
    driver.get(html)
    html1 = driver.page_source
    #overview page
    soup = BeautifulSoup(html1, "lxml")

    box = soup.select_one('div[data-t-obj*="정보"]')
    data["platform_item_id"] = html.split("/")[-1]
    data["title"] = box.select_one("span.font-large3-bold").get_text(strip=True)
    data["author_name"] = box.select_one("span.font-small2").get_text(strip=True)
    data["genre"] = box.select('div.flex.h-16pxr.items-center')[0].get_text(strip=True).replace("웹소설","")
    data["completion_status"] = box.select_one('div.mt-6pxr.flex.items-center').get_text(strip=True)
    data["view_count"] = box.select('div.flex.items-center')[2].get_text(strip=True)

    box = soup.select_one('div[data-t-obj*="회차목록"]').select_one('div[data-t-obj*="eventMeta"]')
    data["first_episode_date"] = datetime.strptime(box.select_one("div.line-clamp-1 span").get_text(strip=True), "%y.%m.%d").date()

    data["episode_count"] = (soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr '
                                             '> div.flex.h-full.flex-1.flex-col > div '
                                             '> div.flex.flex-col.overflow-hidden.mb-28pxr.ml-4px.w-632pxr.rounded-12pxr '
                                             '> div.flex-1.flex.flex-col > div.rounded-b-12pxr.bg-bg-a-20 '
                                             '> div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-20.px-18pxr '
                                             '> div.flex.h-full.flex-1.items-center.space-x-8pxr > span')
                             .get_text(strip=True).replace("전체 ",""))

    #about page
    driver.get(html+"?tab_type=about")
    html2 = driver.page_source
    soup = BeautifulSoup(html2, "lxml")
    data["description"] = soup.select_one('div[data-t-obj*="더보기"]').get_text(strip=True)
    keywords = [
        el.get_text(strip=True)
        for el in soup.select('div[data-t-obj*="테마키워드"]')
        if el
    ]
    data["keywords"] = ",".join(keywords) if keywords else None
    data["age_rating"] = soup.select('span.text-el-70')[-2].get_text(strip=True)
    driver.close()
    return data
