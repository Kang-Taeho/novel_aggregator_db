import pymysql
import time
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#카카오페이지 판타지 등록순
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

#db 저장된 소설 수 가져오기
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM kakaopage_product")
        db_productNum = cursor.fetchone()[0]
except Exception :
    print("sql문 SELECT COUNT(id) FROM kakaopage_product 오류")
finally :
    db.close()

#스크롤 끝까지 내리기
prev_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)

    current_height = driver.execute_script("return document.body.scrollHeight")
    
    if current_height == prev_height :
        time.sleep(1)
        current_height = driver.execute_script("return document.body.scrollHeight")
        if prev_height == current_height :
            break
    prev_height = current_height

# (신작 작품 여부, 15세 이상 작품 여부 , novel_Id, novel_Name ,novel_Visitor) tuple 저장
page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

novelList_id_visitor = []
novel_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-10.px-15pxr > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
novel_Number = int(novel_Number.replace(',','').replace('개',''))

for num in range(1, novel_Number + 1) :

    novel_info = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0}) > div > a > div > div.relative > div.absolute.top-4pxr.right-4pxr.flex.space-x-2pxr'.format(num))
    if novel_info is None :
        age_15gt = False
    else :
        age_15gt = novel_info.select_one('img',{'class':'alt'})['alt']
        if age_15gt == '15세 뱃지' :
            age_15gt = True
        else :
            age_15gt = False

    novel_info = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0}) > div > a > div'.format(num))['data-t-obj']
    novel_Id = novel_info[novel_info.find('"id":"')+6 : novel_info.find('","name')]
    novel_Name = novel_info[novel_info.find('"name":"')+8 : novel_info.find('","subcategory')]


    novel_Visitor = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div:nth-child({0}) > div > a > div > div.h-68pxr.w-full.pt-8pxr.pr-8pxr.pb-4pxr > div.flex.items-center.mt-4pxr > div.text-ellipsis.line-clamp-1.text-el-50.font-x-small1.css-0 > span'.format(num)).get_text()
    mul = 1
    if '만' in novel_Visitor : mul *= 10000
    if '억' in novel_Visitor : mul *= 100000000
    novel_Visitor = novel_Visitor.replace(',','').replace('만','').replace('억','')
    novel_Visitor = float(novel_Visitor) * mul

    if num > (novel_Number - db_productNum) : novelList_id_visitor.append((False,age_15gt,int(novel_Id),novel_Name,novel_Visitor))
    else : novelList_id_visitor.append((True,age_15gt,int(novel_Id),novel_Name,novel_Visitor))
    mul = 1
    
#   title, category, author, keyword, content
try:
    with db.cursor() as cursor :
        for new_work, age_15gt, novel_Id, novel_Name, novel_Visitor in novelList_id_visitor :
            if not new_work :
                sql = """UPDATE kakaopage_product 
                        SET visitor=%s
                        WHERE id=%s 
                """
                val = (novel_Visitor,novel_Id)
                cursor.execute(sql,val)
                db.commit()
                continue
            
            if age_15gt :
                sql = """INSERT INTO kakaopage_product(id,title,category,visitor)
                            VALUES(%s,%s,%s,%s)"""
                val = (novel_Id, novel_Name, "판타지", novel_Visitor)
            else :
                URL_content = "https://page.kakao.com/content/" + str(novel_Id) + "?tab_type=about"

                driver.get(url=URL_content)

                page_source = driver.page_source
                soup_content = BeautifulSoup(page_source,'html.parser')

                novel_Content = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.py-20pxr.pt-31pxr.pb-32pxr > span').get_text()
                novel_Author = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div.mt-4pxr > span').get_text()
                novel_Keyword = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div:nth-child(1) > div.flex.flex-wrap.px-32pxr')
    
                if novel_Keyword is not None :
                    novel_Keyword = novel_Keyword.get_text()
                else :
                    novel_Keyword = None
                
                sql = """INSERT INTO kakaopage_product(id,title,author,category,visitor,keyword,content)
                            VALUES(%s,%s,%s,%s,%s,%s,%s)"""
                val = (novel_Id, novel_Name, novel_Author, "판타지", novel_Visitor, novel_Keyword, novel_Content)
            
            cursor.execute(sql,val)
            db.commit()
finally:
    db.close()
