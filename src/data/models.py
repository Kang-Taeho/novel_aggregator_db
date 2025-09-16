from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Enum, UniqueConstraint, ForeignKey, BigInteger
from datetime import datetime, UTC
from sqlalchemy import Computed

class Base(DeclarativeBase): pass

class Platform(Base):
    __tablename__ = "platforms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)

class Novel(Base):
    __tablename__ = "novels"
    __table_args__ = (UniqueConstraint("normalized_title", "normalized_author", name="uq_canonical"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age_rating: Mapped[str] = mapped_column(Enum("ALL","12","15","19", name="age_rating"), default="ALL")
    completion_status: Mapped[str] = mapped_column(Enum("ongoing","completed","unknown", name="completion_status"), default="unknown")
    mongo_doc_id: Mapped[str | None] = mapped_column(String(24), nullable=True)
    normalized_title: Mapped[str] = mapped_column(
        String(200),
        Computed("LOWER(TRIM(title))", persisted=True),
        nullable=False
    )
    normalized_author: Mapped[str] = mapped_column(
        String(100),
        Computed("LOWER(TRIM(COALESCE(author_name,'')))", persisted=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=lambda: datetime.now(UTC))

class NovelSource(Base):
    __tablename__ = "novel_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id"), nullable=False)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"), nullable=False)
    platform_item_id: Mapped[str] = mapped_column(String(200), nullable=False)
    episode_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_episode_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    view_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
