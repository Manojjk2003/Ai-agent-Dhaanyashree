from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


GeneratedPostStatus = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "scheduled",
    "published",
]


class GeneratedPostCreate(BaseModel):
    run_id: str
    content_plan_id: str
    product_id: str
    product_name: str
    selection_reason: str
    content_type: str
    content_idea: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    poster_prompt: str | None = None
    platforms: list[str] = Field(default_factory=list)
    run_date: date
    status: GeneratedPostStatus = "ready_for_review"
    generation_source: Literal["gemini", "fallback"] = "fallback"


class GeneratedPostUpdate(BaseModel):
    caption: str | None = None
    hashtags: list[str] | None = None
    poster_prompt: str | None = None
    status: GeneratedPostStatus | None = None


class GeneratedPostResponse(GeneratedPostCreate):
    post_id: str
    business_id: str
    scheduled_post_id: str | None = None
    scheduled_at: str | None = None
    created_at: str
    updated_at: str
