from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, env_file_encoding="utf-8")
    MYSQL_DSN: str = None

    MONGODB_URI: str = "mongodb://127.0.0.1:27017"
    MONGODB_DB: str = "novels"
    MONGODB_META_COLLECTION: str = "novel_meta"

    SELENIUM_REMOTE_URL_1: str = "http://localhost:4444/wd/hub"
    SELENIUM_REMOTE_URL_2: str = "http://localhost:4441/wd/hub"
    SELENIUM_REMOTE_URL_3: str = "http://localhost:4442/wd/hub"
    SELENIUM_REMOTE_URL_4: str = "http://localhost:4443/wd/hub"
    HEADLESS: bool = True
    S_USER_AGENT: str | None = None

    R_USER_AGENT : str | None = None

    TZ: str = "Asia/Seoul"
    SCHED_MAX_WORKERS_KP : str = "4"
    SCHED_MAX_WORKERS_NS : str = "8"
    SCHED_TEST_INTERVAL_HOURS : str = "6" #테스트 목적  (실전 0 , 테스트 >0 )
    SCHED_TEST_INTERVAL_SECONDS: str = "0" #테스트 목적  (실전 0 , 테스트 >0 )

    CRON_KAKAOPAGE: str = "0 1 1 * *"
    CRON_NAVERSERIES: str = "0 0 1 * *"
    REQUEST_MIN_INTERVAL_MS: int = 800 #0.8초
    LOG_LEVEL: str = "INFO"

settings = Settings()