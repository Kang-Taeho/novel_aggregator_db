# pages/detail_page.py
from selenium.webdriver.common.by import By
class DetailPage:
    TITLE=(By.CSS_SELECTOR,"[data-testid='title']"); AUTHOR=(By.CSS_SELECTOR,"[data-testid='author']")
    AGE=(By.CSS_SELECTOR,"[data-testid='age-rating']"); STATUS=(By.CSS_SELECTOR,"[data-testid='status']")
    EPISODES=(By.CSS_SELECTOR,"[data-testid='episode-count']")
    def __init__(self, drv, wait): self.drv, self.wait = drv, wait
    def open(self, url): self.drv.get(url)
    def snapshot(self):
        g=lambda loc: (self.drv.find_element(*loc).text or '').strip()
        return {"title":g(self.TITLE),"author_name":g(self.AUTHOR),"age_rating":g(self.AGE) or "ALL","completion_status":(g(self.STATUS) or "unknown").lower(),"episode_count":int((g(self.EPISODES) or "0"))}