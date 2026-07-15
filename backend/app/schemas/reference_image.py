from typing import Literal

from pydantic import BaseModel, Field


ReferenceImageType = Literal["ingredient", "product", "packaging", "style", "other"]


class ReferenceImageCreate(BaseModel):
    name: str = Field(..., min_length=1)
    image_url: str = Field(..., min_length=1)
    reference_type: ReferenceImageType = "ingredient"
    labels: list[str] = Field(default_factory=list)
    notes: str = ""


class ReferenceImageUpdate(BaseModel):
    name: str | None = None
    image_url: str | None = None
    reference_type: ReferenceImageType | None = None
    labels: list[str] | None = None
    notes: str | None = None


class ReferenceImageResponse(ReferenceImageCreate):
    reference_image_id: str
    business_id: str
    created_at: str
    updated_at: str
