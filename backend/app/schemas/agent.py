from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class DailyPlanRequest(BaseModel):
    business_id: str = Field(..., min_length=1)
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
