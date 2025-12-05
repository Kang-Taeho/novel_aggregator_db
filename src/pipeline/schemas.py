# src/pipeline/schemas.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Literal
from datetime import date

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
