from typing import Literal

from pydantic import BaseModel, Field


PosterGenerationSource = Literal["layout", "gemini", "huggingface", "fallback"]
PosterTemplate = Literal[
    "auto",
    "product_spotlight",
    "educational",
    "offer",
    "festival",
]


class GeneratedPosterCreate(BaseModel):
    post_id: str = Field(..., min_length=1)
    template: PosterTemplate = "auto"


class GeneratedPosterResponse(BaseModel):
    poster_id: str
    business_id: str
    post_id: str
    product_id: str
    product_name: str
    prompt: str
    image_url: str
    storage_path: str
    mime_type: str
    provider: PosterGenerationSource
    error_message: str | None = None
    status: Literal["generated"] = "generated"
    created_at: str
    updated_at: str
