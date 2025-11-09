from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.core.config import settings

BLOCK_URL_PATTERNS = [
    "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.svg",
    "*.mp4", "*.webm", "*.m3u8", "*.mp3", "*.wav",
    "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot", "*.ico",
]

@contextmanager
def browser():
    opts = Options()

    # ---- 렌더 최적화 스위치 ----
    if settings.HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-notifications")
    # opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--mute-audio")
    # 이미지 이중 차단(프리페런스 + blink)
    opts.add_argument("--blink-settings=imagesEnabled=false")

    # 네트워크 낭비 줄이기(로그/리포팅 등)
    opts.add_argument("--disable-features=InterestCohort,PrivacySandboxAdsApis,AttributionReporting,Translate,MediaRouter,PaintHolding,BackForwardCache")

    # 필요 시 UA 고정
    if settings.S_USER_AGENT:
        opts.add_argument(f"--user-agent={settings.S_USER_AGENT}")

    # 이미지 비활성(pref 레벨)
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

    # 자동화 흔적/로깅 줄이기(선택)
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    # ---- 페이지 로드 전략: eager ----
    opts.page_load_strategy = "eager"

    drv = webdriver.Remote(
        command_executor=settings.SELENIUM_REMOTE_URL,
        options=opts,
    )

    # ---- 타임아웃/대기 설정 ----
    drv.set_page_load_timeout(20)   # 페이지 네비게이션 타임아웃
    drv.implicitly_wait(0)          # 암묵적 대기는 0 권장(명시적/JS로만 처리)

    try:
        # ---- DevTools로 리소스 차단 ----
        try:
            drv.execute_cdp_cmd("Network.enable", {})
            drv.execute_cdp_cmd("Network.setBlockedURLs", {"urls": BLOCK_URL_PATTERNS})
        except Exception:
            # 원격/버전 환경에 따라 실패할 수 있음 -> 무시하고 진행
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
