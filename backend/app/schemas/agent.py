from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class DailyPlanRequest(BaseModel):
    run_date: date
    platforms: list[str] = Field(default_factory=lambda: ["instagram"])
    require_poster: bool = True


class DailyPlanResponse(BaseModel):
    run_id: str
    content_plan_id: str
    post_id: str
    poster_id: str | None = None
    status: Literal["ready_for_review", "draft"]
    summary: str
    business_name: str
    selected_product_id: str
    selected_product_name: str
    selection_reason: str
    content_type: str
    content_idea: str
    caption: str
    hashtags: list[str]
    poster_prompt: str | None = None
    generation_source: Literal["gemini", "fallback"] = "fallback"
