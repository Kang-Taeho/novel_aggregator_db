from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ListingPage:
    URL = "https://example.com/novels" # 대상에 맞춰 교체
    CARD = (By.CSS_SELECTOR, "[data-testid='novel-card']")


def __init__(self, drv, wait):
    self.drv, self.wait = drv, wait


def open(self):
    self.drv.get(self.URL)
    self.wait.until(EC.presence_of_element_located(self.CARD))


def load_all(self):
    last = 0
    while True:
        self.drv.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        cards = self.drv.find_elements(*self.CARD)
        if len(cards) == last:
            break
    last = len(cards)


def series_ids(self):
    return [c.get_attribute("data-series-id") for c in self.drv.find_elements(*self.CARD) if c.get_attribute("data-series-id")]