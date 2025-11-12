from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(
    settings.MYSQL_DSN,
    pool_size=10,         # 기본 5 → 10
    max_overflow=20,      # 기본 10 → 20
    pool_pre_ping=True,
    future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
