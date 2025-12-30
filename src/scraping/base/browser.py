from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.core.config import settings

# 각 selenium container 용량 분담
GENRE_REMOTE_URLS = {
    "fantasy" : settings.SELENIUM_REMOTE_URL_1,     # 판타지(1.2만개)
    "mo_fantasy" : settings.SELENIUM_REMOTE_URL_2,  # 현판(0.9만개)
    "romance" : settings.SELENIUM_REMOTE_URL_3,     # 로맨스(2.2만개)
    "ro_fantasy" : settings.SELENIUM_REMOTE_URL_4,  # 로판(1만개)
    "wuxia" : settings.SELENIUM_REMOTE_URL_2,       # 무협(0.4만개)
}

BLOCK_URL_PATTERNS = [
    "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.svg",
    "*.mp4", "*.webm", "*.m3u8", "*.mp3", "*.wav",
    "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot", "*.ico",
]

@contextmanager
def browser(genre : str = "", remote_url : str = ""):
    """
    원격 Selenium Chrome WebDriver를 컨텍스트 매니저로 제공한다.
    - genre가 주어지면 GENRE_REMOTE_URLS 기반으로 remote_url을 찾는다.
    - remote_url이 직접 주어지면 그것을 사용한다.
    - 각종 최적화 옵션(이미지/폰트/미디어 차단 등)을 적용한다.
    """
    opts = Options()

    # ---- 성능 및 안정성 관련 옵션 ----
    if settings.HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--mute-audio")
    opts.add_argument("--blink-settings=imagesEnabled=false")

    # ---- 네트워크 낭비 줄이기(로그/리포팅 등) ----
    opts.add_argument("--disable-features=InterestCohort,PrivacySandboxAdsApis,AttributionReporting,Translate,MediaRouter,PaintHolding,BackForwardCache")

    # ---- 필요 시 User-Agent 설정 ----
    if settings.S_USER_AGENT:
        opts.add_argument(f"--user-agent={settings.S_USER_AGENT}")

    # ---- 이미지 비활성(pref 레벨) ----
    opts.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "diagnostics.mode": 0,
    })

    # ---- 자동화 흔적/로깅 줄이기 ----
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    # ---- 크롤링 속도 최적화 ----
    opts.page_load_strategy = "eager"

    if genre :
        drv = webdriver.Remote(
        command_executor=GENRE_REMOTE_URLS[genre],
        options=opts,
        )
    elif remote_url :
        drv = webdriver.Remote(
            command_executor=remote_url,
            options=opts,
        )
    else:
        raise ValueError("browser() requires genre or remote_url")

    # ---- 타임아웃/대기 설정 ----
    drv.set_page_load_timeout(60)
    drv.implicitly_wait(0)

    try:
        # ---- DevTools로 리소스 차단 ----
        try:
            drv.execute_cdp_cmd("Network.enable", {})
            drv.execute_cdp_cmd("Network.setBlockedURLs", {"urls": BLOCK_URL_PATTERNS})
        except Exception:
            pass

        # ---- 애니메이션/트랜지션 제거 ----
        try:
            drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                try {
                  const style = document.createElement('style');
                  style.innerHTML = `
                    * { animation: none !important; transition: none !important; }
                    html, body { scroll-behavior: auto !important; }
                  `;
                  document.documentElement.appendChild(style);
                } catch(e){}
                """
            })
        except Exception:
            pass

        yield drv

    finally:
        drv.quit()
