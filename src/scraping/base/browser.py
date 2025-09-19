from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.core.config import settings

@contextmanager
def browser():
    opts = Options()

    if settings.HEADLESS: opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    if settings.USER_AGENT: opts.add_argument(f"--user-agent={settings.USER_AGENT}")

    drv = webdriver.Remote(command_executor=settings.SELENIUM_REMOTE_URL, options=opts)
    try: yield drv
    finally: drv.quit()
