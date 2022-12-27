import time
import requests
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#카카오페이지 판타지 등록순
URL = "https://page.kakao.com/menu/11/screen/37?subcategory_uid=86&sort_opt=latest"
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920.1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url=URL)

#스크롤 끝까지 내리기
# prev_height = driver.execute_script("return document. body.scrollHeight")
# while True:
#     driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
#     time.sleep(1)

#     current_height = driver.execute_script("return document. body.scrollHeight")
    
#     if current_height == prev_height :
#         break
#     prev_height = current_height

#스크래핑
search_box = driver.find_elements(By.XPATH,'//*[@id="__next"]/div/div[2]/div/div[2]/div[1]/div/div[3]/div/div/div/div[5]/div/a/div')
print(search_box[0].text)