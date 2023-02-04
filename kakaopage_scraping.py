import pymysql
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

sep = "@#$"

# 작품 페이지에서 세부 정보 추출 및 db 저장
# 파일 저장 정보 :  1.15세 뱃지 여부    2.소설 번호     3.소설 제목     4.소설 열람수
# DB 저장 정보 : id title author order category age_gt visitor keyword content
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

f_List = open('kakaopage_product.txt','r',encoding='utf-8').readlines()
db_last_novelId = f_List[0].strip()
del(f_List[0])

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
novel_Order = 0
skip_novel = False
try :
    for f_str in f_List :
        novel_Order += 1

        f_str = f_str.strip().split(sep)
        age_15gt = f_str[0]
        novel_Id = int(f_str[1])
        novel_Name = f_str[2]
        novel_Visitor = int(f_str[3])

        with db.cursor() as cursor :
            # 저장된 소설 visitor 업데이트만 진행
            if novel_Id == 61137409 or skip_novel :
                skip_novel = True
                sql = """UPDATE kakaopage_product
                            SET title=%s, visitor=%s
                            WHERE id=%s
                        """
                val = (novel_Name,novel_Visitor,novel_Id)

                cursor.execute(sql,val)
                db.commit()
                continue

            # 문제점 : 15세 이상 작품 kakaopage 로그인 필요( 보안 문제 )
            if age_15gt == "True" :
                sql = """INSERT INTO kakaopage_product(id,title,latest_order,category,age_gt,visitor)
                            VALUES(%s,%s,%s,%s,%s,%s)"""
                val = (novel_Id, novel_Name, novel_Order, '판타지', 15, novel_Visitor)
                cursor.execute(sql,val)
                db.commit()
                continue
            
            URL_content = "https://page.kakao.com/content/" + str(novel_Id) + "?tab_type=about"
            driver.implicitly_wait(30)
            driver.get(url=URL_content)

            try:
                driver.find_element(By.CSS_SELECTOR,'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.break-keep.py-20pxr.pt-31pxr.pb-32pxr > span')
            except NoSuchElementException :
                driver.refresh()
                driver.find_element(By.CSS_SELECTOR,'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.break-keep.py-20pxr.pt-31pxr.pb-32pxr > span')

            page_source = driver.page_source
            soup_content = BeautifulSoup(page_source,'html.parser')

            novel_Content = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.text-el-60.break-keep.py-20pxr.pt-31pxr.pb-32pxr > span').get_text()
            novel_Author = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2 > div.mt-4pxr > span').get_text()
            
            novel_Keyword = soup_content.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div:nth-child(1) > div.flex.flex-wrap.px-32pxr')
            if novel_Keyword is not None :
                novel_Keyword = novel_Keyword.get_text()
            else :
                novel_Keyword = None

            sql = """INSERT INTO kakaopage_product(id,title,author,latest_order,category,age_gt,visitor,keyword,content)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            val = (novel_Id, novel_Name, novel_Author, novel_Order, '판타지', 0, novel_Visitor, novel_Keyword, novel_Content)

            cursor.execute(sql,val)
            db.commit()
finally :
    db.close()