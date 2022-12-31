import pymysql
import time
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#카카오페이지 판타지 등록순
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM kakaopage_product")
        db_total_productNum = cursor.fetchone()[0]
except(...):
    print("sql문 SELECT COUNT(id) FROM kakaopage_product 오류")
        
#스크롤 끝까지 내리기
prev_height = driver.execute_script("return document. body.scrollHeight")
while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)

    current_height = driver.execute_script("return document. body.scrollHeight")
    
    if current_height == prev_height :
        break
    prev_height = current_height

#스크래핑
#   작품id, visitor
page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

socialList_id_visitor = []
social_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-10.px-15pxr > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
social_Number = int(social_Number.replace(',','').replace('개',''))

for num in range(1, social_Number + 1) :

    social = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0}) > div > a > div'.format(num))
    
    raw_data_str =social['data-t-obj']
    social_Id = raw_data_str[raw_data_str.rfind('"id":"')+6:raw_data_str.find('","name')]

    social_Visitor = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0}) > div > a > div > div.h-68pxr.w-full.pt-8pxr.pr-8pxr.pb-4pxr > div.flex.items-center.mt-4pxr > div.text-ellipsis.line-clamp-1.text-el-50.font-x-small1.css-0 > span'.format(num)).get_text()
    mul = 1
    if '만' in social_Visitor : mul *= 10000
    if '억' in social_Visitor : mul *= 100000000
    social_Visitor = social_Visitor.replace(',','').replace('만','').replace('억','')
    social_Visitor = float(social_Visitor) * mul

    if num > (social_Number - db_total_productNum) : socialList_id_visitor.append((False,int(social_Id),int(social_Visitor)))
    else : socialList_id_visitor.append((True,int(social_Id),int(social_Visitor)))
    mul = 1
    
#   title, category, author, keyword, content
try:
    with db.cursor() as cursor :
        for new_work, social_Id, social_Visitor in socialList_id_visitor :
            if new_work :
                sql = """UPDATE kakaopage_product 
                        SET visitor=%s
                        WHERE id=%s 
                """
                val = (social_Visitor,social_Id)
                cursor.execute(sql,val)
                db.commit()
                continue

            URL_Content = "https://page.kakao.com/content/" + str(social_Id) + "?tab_type=about"

            driver_contnet = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
            driver_contnet.get(url=URL_Content)
             
            page_source = driver_contnet.page_source
            soup_content = BeautifulSoup(page_source,'html.parser')
    
            social_Name = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > span').get_text()
            social_Category = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.mt-16pxr.flex.items-center.justify-center.text-el-60.all-child\:font-small2 > span:nth-child(9)').get_text()
            social_Content = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.py-20pxr.pt-31pxr.pb-32pxr > span').get_text()
            social_Author = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div.mt-4pxr > span').get_text()
            social_Keyword = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div:nth-child(1) > div.flex.flex-wrap.px-32pxr')
    
            if social_Keyword is not None :
                social_Keyword = social_Keyword.get_text()
            else :
                social_Keyword = None
            
            #db 저장
            sql = """INSERT INTO kakaopage_product(id,title,author,category,visitor,keyword,content)
                            VALUES(%s,%s,%s,%s,%s,%s,%s)"""
            val = (social_Id,social_Name,social_Author,social_Category,social_Visitor,social_Keyword,social_Content)
            cursor.execute(sql,val)
            db.commit()
finally:
    db.close()
