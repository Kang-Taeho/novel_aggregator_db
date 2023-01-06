import pymysql
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#노벨피아 판타지 조회순
URL = 'https://novelpia.com/plus/all/view/1/?main_genre=1'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

page_source = driver.page_source
soup = BeautifulSoup(page_source,'html.parser')

total_novelProduct = soup.select_one('body > div.s_dark.plus_top > div.plus-novel-wrapper > div.pc-sort-wrapper.mobile_hidden.s_inv > span').get_text()
total_novelProduct = int(total_novelProduct[total_novelProduct.find("총 ")+2 : total_novelProduct.find("개 작품")].replace(',',''))

novelId_List = []

#모든 페이지 novel id 저장
for page_num in range(1,int(total_novelProduct/30)+2) :
    URL = 'https://novelpia.com/plus/all/view/'+str(page_num)+'/?main_genre=1'
    driver.get(url=URL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    tmp = soup.select_one('body > div.s_dark.plus_top > div.plus-novel-wrapper > div.row').find_all('b',{'class':'name_st'})
    for i in tmp :
        novelId_List.append(str(i)[str(i).find('novel/')+6:str(i).find("';\">")])

#db 저장
for novel_Id in novelId_List :
    URL = 'https://novelpia.com/novel/' + novel_Id
    driver.get(url=URL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    child_num = 46

    novel_Name = soup.select_one('body > div:nth-child({0}) > div.mobile_hidden.s_inv > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > span:nth-child(1)'.format(child_num))
    if novel_Name is None :
        child_num = 47
        novel_Name = soup.select_one('body > div:nth-child({0}) > div.mobile_hidden.s_inv > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > span:nth-child(1)'.format(child_num))
    novel_Name = novel_Name.get_text()
    novel_Author = soup.select_one('body > div:nth-child({0}) > div.mobile_hidden.s_inv > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > font:nth-child(5) > a'.format(child_num)).get_text()
    novel_Category = "판타지"

    novel_info = soup.select_one('body > div:nth-child({0}) > div.mobile_hidden.s_inv > div > div > table > tbody > tr:nth-child(2) > td > div'.format(child_num)).get_text()
    novel_Visitor = novel_info[:novel_info.find('명 ')]
    novel_Visitor = novel_Visitor[novel_Visitor.rfind(' ')+1:].replace(',','')
    novel_Keyword = novel_info[novel_info.rfind('작가태그 :')+6:novel_info.rfind('나만의태그 :')].strip().replace(' ','')
    novel_Content = novel_info[novel_info.find('회\n')+2:novel_info.rfind('작가태그 :')].strip()

    db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
    try:
        with db.cursor() as cursor :
            sql = """INSERT INTO novelpia_product(id,title,author,category,visitor,keyword,content)
                                    VALUES (%s,%s,%s,%s,%s,,%s,%s)
            """
            val = (novel_Id,novel_Name,novel_Author,novel_Category,novel_Visitor,novel_Keyword,novel_Content)
            cursor.execute(sql,val)
            db.commit()
    except Exception:
        db.close()
db.close()