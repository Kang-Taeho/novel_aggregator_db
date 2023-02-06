import pymysql
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

#네이버 시리즈 독점,판타지 최신순
URL = 'https://series.naver.com/search/search.series?t=novel&q=%EB%8F%85%EC%A0%90%2C%ED%8C%90%ED%83%80%EC%A7%80&so=date.dsc&page=1'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.implicitly_wait(30)
driver.get(url=URL)

page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

total_novelNum = soup.select_one('#content > div.com_srch > div.lst_header > h3').get_text()
total_novelNum = int(total_novelNum.replace('웹소설','').replace('(','').replace(')','').replace('\n',''))

#novel_Id 리스트
novel_IdList = []
for page_num in range(1, int(total_novelNum/25) + 2) :
    URL = 'https://series.naver.com/search/search.series?t=novel&q=%EB%8F%85%EC%A0%90%2C%ED%8C%90%ED%83%80%EC%A7%80&so=date.dsc&page=' + str(page_num)
    driver.get(url=URL)

    try:
        driver.find_element(By.CSS_SELECTOR,'#content > div.com_srch > div.bs > ul > li')
    except NoSuchElementException :
        driver.refresh()
        driver.find_element(By.CSS_SELECTOR,'#content > div.com_srch > div.bs > ul > li')

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    if page_num != (int(total_novelNum/25) + 1) :
        for num in range(1,26) :
            novel_Id = soup.select_one('#content > div.com_srch > div.bs > ul > li:nth-child({0}) > div > h3 > a'.format(num))['href']
            novel_Id = novel_Id[novel_Id.find('productNo=')+10:]
            novel_IdList.append(int(novel_Id))
    else :
        for num in range(1,(total_novelNum%25) +1) :
            novel_Id = soup.select_one('#content > div.com_srch > div.bs > ul > li:nth-child({0}) > div > h3 > a'.format(num))['href']
            novel_Id = novel_Id[novel_Id.find('productNo=')+10:]
            novel_IdList.append(int(novel_Id))

#novel 세부 내용 저장
# DB 저장 정보 : id title author first_ep_date category age_gt likeit keyword content
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor :
        sql = "SELECT id FROM naver_series_product"
        cursor.execute(sql)
        db_novel = cursor.fetchall()
        
        novel_Order = 1

        for novel_Id in novel_IdList :
            URL = 'https://series.naver.com/novel/detail.series?productNo=' + str(novel_Id)
            driver.get(url=URL)

            try:
                driver.find_element(By.CSS_SELECTOR,'#content > div.end_head > h2')
            except NoSuchElementException :
                driver.refresh()
                driver.find_element(By.CSS_SELECTOR,'#content > div.end_head > h2')

            page_source = driver.page_source
            soup = BeautifulSoup(page_source,'html.parser')

            novel_Name = soup.select_one('#content > div.end_head > h2').get_text()
            if '[독점]' in novel_Name : novel_Name = novel_Name.replace('[독점]','').strip()
            else : continue

            novel_Likeit = soup.select_one('#content > div.end_head > div.user_action_area > ul > li:nth-child(2) > div > a > em').get_text().replace(',','')
            if '좋아요' in novel_Likeit : novel_Likeit = 0
            else : novel_Likeit = int(novel_Likeit)
            
            # DB 업데이트 : likeit
            if (novel_Id,) in db_novel :    
                sql = """UPDATE naver_series_product
                        SET likeit=%s, latest_order=%s
                        WHERE id=%s"""
                val = (novel_Likeit, novel_Order, novel_Id)
            # DB 저장 : id, title, author, first_ep_date, category, age_gt, score, likeit, content
            else :
                novel_Author = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(3) > a').get_text()
                novel_Category = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(2) > span > a').get_text()
                novel_Score = float(soup.select_one('#content > div.end_head > div.score_area > em').get_text())

                novel_Age = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(5)').get_text()
                if '이용가' not in novel_Age : novel_Age = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(6)').get_text()
                if novel_Age == '전체 이용가' : novel_Age = 0
                else : novel_Age = int(novel_Age.replace('세 이용가',''))
                
                novel_Content = soup.select_one('#content > div.end_dsc > div:nth-child(2)')
                if novel_Content is None : novel_Content = soup.select_one('#content > div.end_dsc > div').get_text()
                else : novel_Content = novel_Content.get_text()
                novel_Content = novel_Content.replace('접기','').strip()

                sql = """INSERT INTO naver_series_product(id,title,author,latest_order,category,age_gt,score,likeit,content)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                val = (novel_Id, novel_Name, novel_Author, novel_Order, novel_Category, novel_Age, novel_Score, novel_Likeit, novel_Content)
            
            cursor.execute(sql,val)
            db.commit()
            novel_Order += 1
finally:
    db.close()