from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import date

"""
크롤링 → 파싱 → 정규화 이후,
DB에 저장되기 전 단계에서 사용하는 **정형화 데이터 스키마**

✔ 파싱 결과에 대한 구조 보장
✔ 필드 타입/제약 조건 검증
✔ 불필요한 필드는 자동 무시 (extra="ignore")
"""

Age = Literal["ALL","12","15","19"]
Status = Literal["ongoing","completed","hiatus","unknown"]

class NovelParsed(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=200)
    author_name: Optional[str] = Field(default=None, max_length=100)
    platform_item_id: str = Field(min_length=1, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=100)
    age_rating: Age = "ALL"
    completion_status: Status = "unknown"
    description: Optional[str] = None
    view_count: Optional[int] = Field(default=None, ge=0)
    episode_count: Optional[int] = Field(default=None, ge=0)
    first_episode_date: Optional[date] = Field(default=None)
    keywords: Optional[List[str]] = Field(default_factory=list)
