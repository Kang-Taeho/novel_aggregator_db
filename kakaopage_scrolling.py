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

sep = "@#$"

# 카카오페이지 판타지 소설 전체 임시 저장 파일
if os.path.isfile('./kakaopage_product.txt') :
    f = open('kakaopage_product.txt','r', encoding='utf-8')
    f.readline()
    db_last_novelId = f.readline().strip().split(sep)[1]
    f.close()
else :
    db_last_novelId = '0'

f = open('kakaopage_product.txt','w', encoding='utf-8')
f.write(db_last_novelId + '\n')

# 카카오페이지 판타지 등록순
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

# 스크롤 저장되지 않은 소설 까지 내리기
# 문제점 : 너무 긴 로딩 시간
page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

novel_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-10.px-15pxr > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
novel_Number = int(novel_Number.replace(',','').replace('개',''))

scroll_pos = driver.find_element(By.TAG_NAME,'body')
sleep_sec = 0.5
while True:
    for i in range(1,30) :
        time.sleep(sleep_sec)
        scroll_pos.send_keys(Keys.PAGE_DOWN)
        scroll_pos.send_keys(Keys.PAGE_DOWN)
    
    try :
        if driver.find_element(By.CSS_SELECTOR,'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0})'.format(novel_Number)) :
            break
    except NoSuchElementException :
        if sleep_sec <= 5 : sleep_sec += 0.5

# 작품 전체 페이지에서 정보 추출
# 1.15세 뱃지 여부    2.소설 번호     3.소설 제목     4.소설 열람수
WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div')))

page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

novel_infos = soup.select('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div')

for novel_info in novel_infos :
    age_15gt =  False
    for badge in novel_info.select('img',{'class':'alt'}):
        if badge['alt'] == "15세 뱃지" : age_15gt = True
    
    novel_Id = novel_info.select_one('a')['href']
    novel_Id = novel_Id[novel_Id.rfind('/')+1:]

    novel_Visitor =  novel_info.select_one('span').get_text()
    novel_Name = novel_info.get_text().replace(novel_Visitor,'').replace('[연재]','').replace('[완결]','').strip()

    mul = 1
    if '만' in novel_Visitor : mul *= 10000
    if '억' in novel_Visitor : mul *= 100000000
    novel_Visitor = novel_Visitor.replace(',','').replace('만','').replace('억','')
    novel_Visitor = int(float(novel_Visitor) * mul)

    if '[단행본]' not in novel_Name :
        f.write(str(age_15gt) + sep + novel_Id + sep + novel_Name + sep + str(novel_Visitor) + '\n')
f.close()