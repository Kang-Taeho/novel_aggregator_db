import pymysql
import time
import re
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 카카오페이지 판타지 등록순
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

# mysql 저장된 소설 수 가져오기
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM kakaopage_product")
        db_productNum = cursor.fetchone()[0]
except Exception :
    print("SELECT COUNT(id) FROM kakaopage_product 오류")
finally :
    db.close()

# 스크롤 끝까지 내리기
prev_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)
    current_height = driver.execute_script("return document.body.scrollHeight")
    
    if current_height == prev_height :
        time.sleep(2)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        current_height = driver.execute_script("return document.body.scrollHeight")

        if prev_height == current_height :
            break
    time.sleep(1)
    prev_height = current_height
    
# 작품 전체 페이지에서 정보 추출
# 1.db 저장된 소설 여부      2.15세 뱃지 여부    3.소설 번호     4.소설 제목     5.소설 열람수 
page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

novelList_id_visitor = []
novel_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-10.px-15pxr > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
novel_Number = int(novel_Number.replace(',','').replace('개',''))

novel_info_List = []
novel_infos = soup.select('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.flex.grow.flex-col > div > div.flex.grow.flex-col.py-10pxr.px-15pxr > div > div > div > div')
iter_num = 0

for novel_info in novel_infos :
    iter_num += 1
    if iter_num > (novel_Number - db_productNum) : new_work = False
    else : new_work = True

    age_15gt =  False
    for badge in novel_info.select('img',{'class':'alt'}):
        if badge['alt'] == "15세 뱃지" : age_15gt = True
    
    novel_Id = novel_info.select_one('a')['href']
    novel_Id = novel_Id[novel_Id.rfind('/')+1:]

    novel_Visitor =  novel_info.select_one('span').get_text()
    novel_Name = novel_info.get_text().replace(novel_Visitor,'')

    mul = 1
    if '만' in novel_Visitor : mul *= 10000
    if '억' in novel_Visitor : mul *= 100000000
    novel_Visitor = novel_Visitor.replace(',','').replace('만','').replace('억','')
    novel_Visitor = int(float(novel_Visitor) * mul)

    novel_info_List.append((new_work, age_15gt, novel_Id, novel_Name, novel_Visitor))
    
#   title, category, author, keyword, content
# try:
#     with db.cursor() as cursor :
#         for new_work, novel_Age, novel_Id, novel_Name, novel_Visitor in novelList_id_visitor :
#             if not new_work :
#                 sql = """UPDATE kakaopage_product 
#                         SET visitor=%s
#                         WHERE id=%s 
#                 """
#                 val = (novel_Visitor,novel_Id)
#                 cursor.execute(sql,val)
#                 db.commit()
#                 continue
            
#             if "[단행본]" in novel_Name :
#                 sql = """INSERT INTO kakaopage_product(id,title,category,age_gt,visitor)
#                             VALUES(%s,%s,%s,%s)"""
#                 val = (novel_Id, novel_Name, "판타지", novel_Age, novel_Visitor)

#                 cursor.execute(sql,val)
#                 db.commit()
#                 continue
            
#             if novel_Age == 15 :
#                 sql = """INSERT INTO kakaopage_product(id,title,category,age_gt,visitor)
#                             VALUES(%s,%s,%s,%s)"""
#                 val = (novel_Id, novel_Name, "판타지", novel_Age, novel_Visitor)
#             else :
#                 URL_content = "https://page.kakao.com/content/" + str(novel_Id) + "?tab_type=about"

#                 driver.get(url=URL_content)

#                 page_source = driver.page_source
#                 soup_content = BeautifulSoup(page_source,'html.parser')

#                 novel_Content = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.py-20pxr.pt-31pxr.pb-32pxr > span').get_text()
#                 novel_Author = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div.mt-4pxr > span').get_text()
#                 novel_Keyword = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div:nth-child(1) > div.flex.flex-wrap.px-32pxr')
    
#                 if novel_Keyword is not None :
#                     novel_Keyword = novel_Keyword.get_text()
#                 else :
#                     novel_Keyword = None
                
#                 sql = """INSERT INTO kakaopage_product(id,title,author,category,visitor,keyword,content)
#                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
#                 val = (novel_Id, novel_Name, novel_Author, "판타지", novel_Age, novel_Visitor, novel_Keyword, novel_Content)
            
#             cursor.execute(sql,val)
#             db.commit()
# finally:
#     db.close()
