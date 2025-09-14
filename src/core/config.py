from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, env_file_encoding="utf-8")
    MYSQL_DSN: str
    MONGODB_URI: str = "mongodb://127.0.0.1:27017"
    MONGODB_DB: str = "novels"
    MONGODB_META_COLLECTION: str = "novel_meta"
    SELENIUM_REMOTE_URL: str = "http://localhost:4444/wd/hub"
    HEADLESS: bool = True
    USER_AGENT: str | None = None
    TZ: str = "Asia/Seoul"
    CRON_KAKAOPAGE: str = "10 3 * * *"
    CRON_NAVERSERIES: str = "40 3 * * *"
    CRON_MUNPIA: str = "10 4 * * *"
    REQUEST_MIN_INTERVAL_MS: int = 800
    LOG_LEVEL: str = "INFO"

settings = Settings()