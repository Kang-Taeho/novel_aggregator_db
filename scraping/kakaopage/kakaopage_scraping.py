import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from kakaopage_scrolling import scrolling
from kakaopage_DB import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 중요 변수
id_age_new_list = []

# id_age_new_list : scraping 필요한 소설 리스트
#신작
start = time.time()
id_age_new_list += scrolling()
end = time.time()
print("스크롤 함수 측정 시간 : " + str(end-start) + "초") ############################

#구작
now = datetime.now(timezone('Asia/Seoul'))
criteria = now.date() - relativedelta(years=1)
with db.cursor() as cursor :
    sql = """SELECT id, age_15gt, 0 
            FROM kakaopage_product
            WHERE latest_ep_date BETWEEN %s AND %s
        """
    val = (criteria,now)
    cursor.execute(sql,val)
    id_age_new_list += list(cursor.fetchall())

#사전 작업
#1
f = open('kakaopage_pre_latest_novel_id.txt','w', encoding='utf-8')
f.write(str(id_age_new_list[0][0]))

# scraping 시작
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.implicitly_wait(5)

for Novel_Info.Id, Novel_Info.Age_15gt, Novel_Info.new_work in id_age_new_list :

    print(str(Novel_Info.Id)) ##########################

    if Novel_Info.Age_15gt :
        start = time.time()
        if Novel_Info.new_work : DB_Insert()
        else : DB_Update()
        end = time.time()
        print("15세 이상 시간 : " + str(end-start) + "초\n") #######################
        continue
    
    start = time.time()
    URL_content = "https://page.kakao.com/content/" + str(Novel_Info.Id)
    driver.get(url=URL_content)
    
    try:
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[1]')))
    except TimeoutException :
        driver.refresh()
        try :
            driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[1]')
        except NoSuchElementException :
                if driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/div[1]').text == "해당하는 작품이 없습니다" :
                    DB_Delete()
                    print("제거")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    if Novel_Info.new_work : 
        novel_Title = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > span').get_text()
        novel_Author = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div.mt-4pxr').get_text()
        if '[단행본]' in novel_Title : continue
        novel_First_ep_date = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) > div:nth-child(1) > div.min-h-360pxr > ul > li:nth-child(1) > div > div > a > div > div.flex.flex-col > div.text-ellipsis.line-clamp-1.font-small2.text-el-60').get_text()

        # 소설 정보
        Novel_Info.Author = novel_Author.strip()
        Novel_Info.Title = novel_Title.replace('(소설)','').replace('[연재]','').replace('[완결]','').strip()
        Novel_Info.First_ep_date = novel_First_ep_date[:10]

    novel_Completion_status = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div:nth-child(1) > span').get_text()
    novel_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) > div:nth-child(1) > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.px-15pxr.bg-bg-a-20 > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
    novel_Visitor = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.mt-16pxr.flex.items-center.justify-center.text-el-60.all-child\:font-small2 > span:nth-child(2)').get_text()
    mul = 1
    if '만' in novel_Visitor : mul *= 10000
    if '억' in novel_Visitor : mul *= 100000000
    novel_Visitor = novel_Visitor.replace(',','').replace('만','').replace('억','')
    
    # 소설 정보
    Novel_Info.Img_url = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.mx-auto.css-1cyn2un-ContentOverviewThumbnail > div > div > img')['src']
    Novel_Info.Number = novel_Number.replace('전체','').replace(',','').strip()
    Novel_Info.Visitor = int(float(novel_Visitor) * mul)
    if '연재' in novel_Completion_status : Novel_Info.Completion_status = 0
    elif '완결' in novel_Completion_status : Novel_Info.Completion_status = 1

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div'))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div[1]/div[3]/div[2]'))).click()
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[1]')))

    novel_Latest_ep_date = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[1]/div/div/a/div/div[2]/div[2]').text

    URL_content = "https://page.kakao.com/content/" + str(Novel_Info.Id) + "?tab_type=about"
    driver.get(url=URL_content)

    # 소설 정보
    try:
        novel_Keyword = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]').text
        novel_Description = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[3]/span').text
        Novel_Info.Keyword = novel_Keyword.replace('\n','')
    except NoSuchElementException :
        novel_Description = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/span').text
        Novel_Info.Keyword = None
    Novel_Info.Description = novel_Description.replace('\n','')
    Novel_Info.Latest_ep_date = novel_Latest_ep_date[:10]

    end = time.time()
    print("스크래핑 실행시간 : " + str(end-start) + "초\n") #######################

    if Novel_Info.new_work : 
        start = time.time()
        DB_Insert()
        end = time.time()
        print("DB 삽입 실행 시간 : " + str(end-start) + "초\n") #######################
    else :
        start = time.time()
        DB_Update()
        end = time.time()
        print("DB 업데이트 실행 시간 : " + str(end-start) + "초\n") #######################

db.close()