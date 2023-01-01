import pymysql
import time
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#네이버 시리즈 최신순
URL = 'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=202&page=1'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

total_novelProduct = soup.select_one('#content > div > div > div.total').get_text()
total_novelProduct = int(total_novelProduct.replace('총','').replace(',','').replace('개 작품',''))

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor :
        for page_num in range(1,int(total_novelProduct/25) + 2) :
            URL = 'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=202&page=' + str(page_num)
            driver.get(url=URL)

            list_view = driver.find_element(By.XPATH,'//*[@id="list"]')
            list_view.click()

            page_source = driver.page_source
            soup = BeautifulSoup(page_source,'html.parser')

            if page_num != (int(total_novelProduct/25) + 1) :
                    for num in range(1,26) :
                        novel_Id = soup.select_one('#content > div > ul > li:nth-child({0}) > a'.format(num))['href']
                        novel_Id = novel_Id[novel_Id.find('productNo=')+10:]
                        novel_Name = soup.select_one('#content > div > ul > li:nth-child({0}) > div > h3 > a'.format(num)).get_text()
                        novel_Author = soup.select_one('#content > div > ul > li:nth-child({0}) > div > p.info > span.author'.format(num)).get_text()
                        novel_Content = soup.select_one('#content > div > ul > li:nth-child({0}) > div > p.dsc'.format(num)).get_text().strip()
                        
                        sql = """INSERT INTO naver_series_product(id,title,author,category,content)
                                    VALUES (%s,%s,%s,%s,%s)
                        """
                        val = (novel_Id,novel_Name,novel_Author,"판타지",novel_Content)
                        cursor.execute(sql,val)
                        db.commit()
            else :
                for num in range(1,(total_novelProduct%25) +1) :
                    novel_Id = soup.select_one('#content > div > ul > li:nth-child({0}) > a'.format(num))['href']
                    novel_Id = novel_Id[novel_Id.find('productNo=')+10:]
                    novel_Name = soup.select_one('#content > div > ul > li:nth-child({0}) > div > h3 > a'.format(num)).get_text()
                    novel_Author = soup.select_one('#content > div > ul > li:nth-child({0}) > div > p.info > span.author'.format(num)).get_text()
                    novel_Content = soup.select_one('#content > div > ul > li:nth-child({0}) > div > p.dsc'.format(num)).get_text().strip()
                        
                    sql = """INSERT INTO naver_series_product(id,title,author,category,content)
                                    VALUES (%s,%s,%s,%s,%s)
                    """
                    val = (novel_Id,novel_Name,novel_Author,"판타지",novel_Content)
                    cursor.execute(sql,val)
                    db.commit()
finally:
    db.close()