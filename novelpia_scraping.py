import pymysql
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
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

novel_infoList = []

#모든 페이지 novel id,novel_book,novel_visitor 저장
for page_num in range(1,2) : #int(total_novelProduct/30)+2
    URL = 'https://novelpia.com/plus/all/view/'+str(page_num)+'/?main_genre=1'
    driver.get(url=URL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    tmp = soup.select_one('body > div.s_dark.plus_top > div.plus-novel-wrapper > div.row').find_all('b',{'class':'name_st'})
    for i in tmp :
        mul = 1
        novel_Id = int(str(i)[str(i).find('novel/')+6:str(i).find("';\">")])

        novel_info = soup.select_one('body > div.s_dark.plus_top > div.plus-novel-wrapper > div.row > div.col-md-12.novelbox.mobile_hidden.novel_{0}.s_inv > table > tbody > tr:nth-child(1) > td.info_st > span.info_t_box'.format(novel_Id)).get_text()
        novel_Visitor = novel_info[:novel_info.find('명')].replace('\n','').strip()
        if 'M' in novel_Visitor :
            novel_Visitor = novel_Visitor.replace('M','') 
            mul *= 1000000
        elif 'K' in novel_Visitor :
            novel_Visitor = novel_Visitor.replace('K','')
            mul *= 1000
        novel_Visitor = int(float(novel_Visitor) * mul)
        
        novel_Book = int(novel_info[novel_info.find('명')+1:novel_info.find('회차')].replace('\n','').replace(',','').strip())

        novel_infoList.append((novel_Id,novel_Book,novel_Visitor))
        
        
#db 저장
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='trigger3587!',db='product',charset='utf8')
try:
    with db.cursor() as cursor : 
        sql = "SELECT id FROM novelpia_product"
        cursor.execute(sql)
        db_novel = cursor.fetchall()

        for novel_Id,novel_Book,novel_Visitor in novel_infoList :
            if (novel_Id,) in db_novel :
                sql = """UPDATE novelpia_product
                            SET visitor=%s
                            WHERE id=%s"""
                val = (novel_Visitor,novel_Id)
            
            else :
                URL = 'https://novelpia.com/novel/' + str(novel_Id)
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
                novel_Keyword = novel_info[novel_info.rfind('작가태그 :')+6:novel_info.rfind('나만의태그 :')].strip().replace(' ','')
                novel_Content = novel_info[novel_info.find('회\n')+2:novel_info.rfind('작가태그 :')].strip()

                sql = """INSERT INTO novelpia_product(id,title,author,category,visitor,keyword,content)
                                     VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                val = (novel_Id,novel_Name,novel_Author,novel_Category,novel_Visitor,novel_Keyword,novel_Content)
            
            cursor.execute(sql,val)
            db.commit()
finally :
    db.close()