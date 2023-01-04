import pymysql
from bs4 import BeautifulSoup
import time

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


#문피아 선독점 (판타지, 새작품순)
URL = 'https://novel.munpia.com/page/hd.platinum/group/pl.serial/exclusive/true/view/allend'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(url=URL)

WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/section/section[1]/ul/li[3]/a"))).click()
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/section/section[2]/ul[1]/li[4]"))).click()
time.sleep(2)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/section/section[3]/div[1]/a"))).click()
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/section/section[3]/nav/ul/li[3]"))).click()
time.sleep(2)

page_index = 0
novel_IdList = []
while True :
    if page_index != 6 : page_index += 1

    try : 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="NOVELOUS-CONTENTS"]/section[4]/ul/li[{0}]'.format(page_index)))).click()
        time.sleep(1)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source,'html.parser')

        novels = soup.select_one('#SECTION-LIST > ul')
        novel_Ids = novels.find_all('a',{'class' : 'title col-xs-6'})
        for novel_Id in novel_Ids :
            novel_Id = novel_Id['href']
            novel_Id = novel_Id[ novel_Id.rfind('/')+1 : ]
            novel_IdList.append(int(novel_Id))

    except Exception :
        break
print(len(novel_IdList))





