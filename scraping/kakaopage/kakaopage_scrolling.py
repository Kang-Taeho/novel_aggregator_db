import time
import os.path
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def scrolling() :
    scroll_info_list = []

    # 최신 스크래핑 소설 정보 찾기
    if os.path.isfile('./kakaopage_pre_latest_novel_id.txt') :
        f = open('kakaopage_pre_latest_novel_id.txt','r', encoding='utf-8')
        db_last_novelId = int(f.readline())
        f.close()
    else :
        # 가장 오래된 판타지 소설 : 달빛조각사 id(29226849)
        db_last_novelId = 29226849

    # 카카오페이지 판타지 등록순
    URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-logging"])
    # options.add_argument('--blink-settings=imagesEnabled=false')  15세 뱃지 여부 판단으로 이미지 로드 필요
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get(url=URL)

    # scrolling : 최신 스크래핑한 소설 까지 내리기
    # 문제점 : 동적페이지 로딩 시간
    scroll_pos = driver.find_element(By.TAG_NAME,'body')
    sleep_sec = 0.5
    while True:
        for i in range(1,10) :
            time.sleep(sleep_sec)
            scroll_pos.send_keys(Keys.PAGE_DOWN)
            scroll_pos.send_keys(Keys.PAGE_DOWN)

        try :
            if driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div/div[2]/div[1]/div/div[3]/div/div/div/div/div/a[contains(@href,"{0}")]'.format("/content/"+str(db_last_novelId))) :
                break
        except NoSuchElementException :
           if sleep_sec <= 5 : sleep_sec += 0.1


    # 작품 전체 페이지에서 정보 추출
    # 1.신작 작품 여부  2.15세 뱃지 여부    3.소설 번호
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div')))

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    novel_infos = soup.select('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div')

    for novel_info in novel_infos :
        age_15gt =  0
        for badge in novel_info.select('img',{'class':'alt'}):
           if badge['alt'] == "15세 뱃지" : age_15gt = 1

        novel_Id = novel_info.select_one('a')['href']
        novel_Id = int(novel_Id[novel_Id.rfind('/')+1:])

        if novel_Id == db_last_novelId : break

        scroll_info_list.append((novel_Id, 1))
        
    driver.close()
    return scroll_info_list