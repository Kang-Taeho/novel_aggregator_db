from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, env_file_encoding="utf-8")
    MYSQL_DSN: str = None

    MONGODB_URI: str = "mongodb://127.0.0.1:27017"
    MONGODB_DB: str = "novels"
    MONGODB_META_COLLECTION: str = "novel_meta"

    SELENIUM_REMOTE_URL: str = "http://localhost:4444/wd/hub"
    HEADLESS: bool = True
    S_USER_AGENT: str | None = None

    R_USER_AGENT : str | None = None

    TZ: str = "Asia/Seoul"
    SCHED_MAX_WORKERS : str = "8"
    SCHED_TEST_INTERVAL_HOURS : str = "6" #테스트 목적  (실전 0 , 테스트 >0 )
    SCHED_TEST_INTERVAL_SECONDS: str = "0" #테스트 목적  (실전 0 , 테스트 >0 )

    CRON_KAKAOPAGE: str = "0 1 1 * *"
    CRON_NAVERSERIES: str = "0 0 1 * *"
    REQUEST_MIN_INTERVAL_MS: int = 800 #0.8초
    LOG_LEVEL: str = "INFO"

settings = Settings()