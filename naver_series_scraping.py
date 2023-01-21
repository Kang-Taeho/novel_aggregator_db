import pymysql
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#네이버 시리즈 독점,판타지 판매순
URL = 'https://series.naver.com/search/search.series?t=novel&q=%EB%8F%85%EC%A0%90%2C%ED%8C%90%ED%83%80%EC%A7%80&so=selling.dsc&page=1'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

total_novelNum = soup.select_one('#content > div.com_srch > div.lst_header > h3').get_text()
total_novelNum = int(total_novelNum.replace('웹소설','').replace('(','').replace(')','').replace('\n',''))

#novel_Id 리스트
novel_IdList = []
for page_num in range(1, int(total_novelNum/25) + 2) : 
    URL = 'https://series.naver.com/search/search.series?t=novel&q=%EB%8F%85%EC%A0%90%2C%ED%8C%90%ED%83%80%EC%A7%80&so=selling.dsc&page=' + str(page_num)
    driver.get(url=URL)

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
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')

try:
    with db.cursor() as cursor :
        sql = "SELECT id FROM naver_series_product"
        cursor.execute(sql)
        db_novel = cursor.fetchall()

        for novel_Id in novel_IdList :
            URL = 'https://series.naver.com/novel/detail.series?productNo=' + str(novel_Id)
            driver.get(url=URL)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source,'html.parser')

            if (novel_Id,) in db_novel :
                novel_Likeit = soup.select_one('#content > div.end_head > div.user_action_area > ul > li:nth-child(2) > div > a > em').get_text().replace(',','')
                
                sql = """UPDATE naver_series_product
                        SET likeit=%s
                        WHERE id=%s"""
                val = (novel_Likeit,novel_Id)

            else :
                novel_Name = soup.select_one('#content > div.end_head > h2').get_text()
                if '[독점]' in novel_Name :
                    novel_Name = novel_Name.replace('[독점]','').strip()
                else :
                    continue

                novel_Author = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(3) > a').get_text()
                novel_Category = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(2) > span > a').get_text()
                novel_Likeit = soup.select_one('#content > div.end_head > div.user_action_area > ul > li:nth-child(2) > div > a > em').get_text().replace(',','')
                novel_Age = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(5)').get_text()
                if '이용가' not in novel_Age :
                    novel_Age = soup.select_one('#content > ul.end_info.NE\=a\:nvi > li > ul > li:nth-child(6)').get_text()
                if novel_Age == '15세 이용가' : novel_Age = 15
                elif novel_Age == '전체 이용가' : novel_Age = 0
                novel_Content = soup.select_one('#content > div.end_dsc > div:nth-child(2)')
                if novel_Content is None :
                    novel_Content = soup.select_one('#content > div.end_dsc > div').get_text()
                else :
                    novel_Content = novel_Content.get_text()
                novel_Content = novel_Content.replace('접기','').strip()

                sql = """INSERT INTO naver_series_product(id,title,author,category,age_gt,likeit,content)
                            VALUES (%s,%s,%s,%s,%s,%s)"""
                val = (novel_Id,novel_Name,novel_Author,novel_Category,novel_Age,novel_Likeit,novel_Content)

            cursor.execute(sql,val)
            db.commit()


finally:
    db.close()