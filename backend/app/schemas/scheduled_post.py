from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


ScheduledPostStatus = Literal["scheduled", "published", "cancelled", "failed"]


class ScheduledPostCreate(BaseModel):
    post_id: str = Field(..., min_length=1)
    scheduled_at: datetime
    platforms: list[str] = Field(default_factory=lambda: ["instagram"])


class ScheduleRecommendationRequest(BaseModel):
    post_id: str = Field(..., min_length=1)
    target_date: date | None = None
    platforms: list[str] = Field(default_factory=lambda: ["instagram"])


class ScheduleRecommendationResponse(BaseModel):
    recommended_at: str
    reason: str
    confidence: float = Field(..., ge=0, le=1)
    alternative_slots: list[str] = Field(default_factory=list)
    generation_source: Literal["gemini", "fallback"] = "fallback"


class ScheduledPostResponse(BaseModel):
    scheduled_post_id: str
    business_id: str
    post_id: str
    product_id: str
    product_name: str
    content_type: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    poster_prompt: str | None = None
    platforms: list[str] = Field(default_factory=list)
    scheduled_at: str
    status: ScheduledPostStatus = "scheduled"
    created_at: str
    updated_at: str
