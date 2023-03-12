import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from kakaopage_scrolling import scrolling
from kakaopage_DB import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from security.setting import LOGIN

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

# 중요 변수
insert_novel_info_Tlist = []
update_novel_info_Tlist = []
id_new_list = []

# # id_new_list : scraping 필요한 소설 리스트
# #신작
# # scrolling()
f = open('kakaopage_scrolling.txt','r', encoding='utf-8')
for line in f.readlines() : id_new_list.append((int(line.strip()),1))
f.close()

# #구작
now = datetime.now(timezone('Asia/Seoul'))
criteria = now.date() - relativedelta(years=1)

db = pymysql.connect(host=Test_DB.host,port=Test_DB.port,user=Test_DB.user,passwd=Test_DB.passwd,db=Test_DB.db,charset='utf8')
with db.cursor() as cursor :
    sql = """SELECT id, 0 
            FROM kakaopage_product
            WHERE latest_ep_date BETWEEN %s AND %s
        """
    val = (criteria,now)
    cursor.execute(sql,val)
    id_new_list += list(cursor.fetchall())
db.close()

# #사전 작업
# #1
f = open('kakaopage_pre_latest_novel_id.txt','w', encoding='utf-8')
f.write(str(id_new_list[0][0]))
f.close()

# # scraping 시작
options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/110.0.5481.180 Safari/537.36'
options.add_experimental_option("excludeSwitches",["enable-logging"])
options.add_argument('user-agent=' + user_agent)
options.add_argument('--start-maximized')
options.add_argument("--disable-extensions")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

# # 15세 이상 작품 열람을 위한 로그인
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"
driver.get(url=URL)

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[1]/div/div[1]/div[3]/div/img'))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="loginKey--1"]')))
driver.find_element(By.XPATH,'//*[@id="loginKey--1"]').send_keys(LOGIN.get_id())
driver.find_element(By.XPATH,'//*[@id="password--2"]').send_keys(LOGIN.get_pw())

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent"]/div/div/form/div[4]/button[1]'))).click()
time.sleep(3)

for Novel_Info.Id, Novel_Info.new_work in id_new_list :
    print(str(Novel_Info.Id)) ######################################

    start = time.time()
    URL_content = "https://page.kakao.com/content/" + str(Novel_Info.Id)
    driver.get(url=URL_content)
    
    if Novel_Info.new_work:
        # 무료 대여권 창 없애기
        try : WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div[2]/button'))).click()
        except Exception : pass

        # 단행본 넘기기 1차
        try :
            if  '[단행본]' in driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[3]/div[2]/span').text :
                continue
        except Exception : pass

    for i in range(10):
        try:
            # if i < 5 :WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]'))).click()
            # else :
            #     WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]')))
            #     element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]')
            #     driver.execute_script("arguments[0].click();", element)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]'))).click()
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div[1]/div[3]/div[2]'))).click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[1]/div/div/a/div/div[2]/div[2]')))
            break
        except  Exception :
            # 소설이 없어졌을 경우
            try :
                WebDriverWait(driver, 3).until(EC.presence_of_element_located(By.XPATH,'//*[@id="__next"]/div/div/div[1]'))
                if driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/div[1]').text == "해당하는 작품이 없습니다" : DB_Delete(); break; print("제거") #####################
            except Exception as e : 
                if i == 9 : raise(e)
            # loading 상태 해결
            driver.refresh()
        print("반복1")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')

    novel = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0')
    novel_Title = novel.select_one('div.relative.text-center.mx-32pxr.py-24pxr > span').get_text()
    # 단행본 넘기기 2차
    if '[단행본]' in novel_Title : continue
    novel_Img_url = novel.select_one('div.mx-auto.css-1cyn2un-ContentOverviewThumbnail > div > div > img')['src']

    novel_1 = novel.select_one('div.relative.text-center.mx-32pxr.py-24pxr > div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50.opacity-100.all-child\:font-small2')
    novel_Author = novel_1.select_one('div.mt-4pxr').get_text()
    novel_Completion_status = novel_1.select_one('div:nth-child(1) > span').get_text()
    
    novel_2 = novel.select_one('div.relative.text-center.mx-32pxr.py-24pxr > div.mt-16pxr.flex.items-center.justify-center.text-el-60.all-child\:font-small2')
    novel_Age15gt = novel_2.select_one('span:nth-child(7)').get_text()
    novel_Visitor = novel_2.select_one('span:nth-child(2)').get_text()
    
    novel_Number = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) > div:nth-child(1) > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.px-15pxr.bg-bg-a-20 > div.flex.h-full.flex-1.items-center.space-x-8pxr > span').get_text()
    novel_Latest_ep_date = soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) > div:nth-child(1) > div.min-h-360pxr > ul > li:nth-child(1) > div > div > a > div > div.flex.flex-col > div.text-ellipsis.line-clamp-1.font-small2.text-el-60').get_text()
   
    mul = 1
    if '만' in novel_Visitor : mul *= 10000
    if '억' in novel_Visitor : mul *= 100000000
    novel_Visitor = novel_Visitor.replace(',','').replace('만','').replace('억','')
    
    # 소설 정보
    Novel_Info.Title = novel_Title.replace('(소설)','').replace('[연재]','').replace('[완결]','').strip()
    Novel_Info.Author = novel_Author.strip()
    Novel_Info.Img_url = novel_Img_url.strip()
    Novel_Info.Number = novel_Number.replace('전체','').replace(',','').strip()
    Novel_Info.Latest_ep_date = novel_Latest_ep_date.strip()
    Novel_Info.Visitor = int(float(novel_Visitor) * mul)
    if '15세' in novel_Age15gt : Novel_Info.Age_15gt = 1
    else : Novel_Info.Age_15gt = 0
    if '연재' in novel_Completion_status : Novel_Info.Completion_status = 0
    elif '완결' in novel_Completion_status : Novel_Info.Completion_status = 1
               
    if Novel_Info.new_work :
        for i in range(10) :
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[2]/a/div'))).click()                                                                            
                WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element_attribute((By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[1]/div/div/div[2]/a/div/div/span'),'class','text-ellipsis line-clamp-1 font-small1-bold text-el-20 css-1797ph-Text'))
                break
            except Exception as e :
                driver.refresh()
                if i == 9 : raise(e)
            print("반복2")

        about_page_source = driver.page_source
        about_soup = BeautifulSoup(about_page_source,'html.parser')
     
        novel = about_soup.select_one('#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20')
        novel_Description = novel.select_one('div.text-el-60.break-keep.py-20pxr.pt-31pxr.pb-32pxr > span').get_text()
        novel_Keyword = novel.select_one('div:nth-child(1) > div.flex.flex-wrap.px-32pxr')

        # 소설 정보
        # 키워드가 있는 경우
        Novel_Info.Description = novel_Description.replace('\n','').strip()
        if novel_Keyword :
            Novel_Info.Keyword = novel_Keyword.get_text().replace('\n','').strip()
        else :
            Novel_Info.Keyword = None

    if Novel_Info.new_work : 
        insert_novel_info_Tlist.append( (Novel_Info.Id, Novel_Info.Title, Novel_Info.Author, Novel_Info.Img_url, 
                                         Novel_Info.Description, Novel_Info.Age_15gt, Novel_Info.Completion_status, Novel_Info.Number,
                                        Novel_Info.Latest_ep_date, Novel_Info.Visitor, Novel_Info.Keyword)) #11개
    else :
        update_novel_info_Tlist.append((Novel_Info.Id, Novel_Info.Title, Novel_Info.Author, Novel_Info.Img_url, 
                                        Novel_Info.Age_15gt, Novel_Info.Completion_status, Novel_Info.Number, 
                                        Novel_Info.Latest_ep_date, Novel_Info.Visitor)) #9개
start = time.time()
DB_Insert_Many(insert_novel_info_Tlist)
end = time.time()
print("DB 삽입 실행 시간 : " + str(end-start) + "초\n") #######################

start = time.time()
DB_Update_Many(update_novel_info_Tlist)
end = time.time()
print("DB 업데이트 실행 시간 : " + str(end-start) + "초\n") #######################
