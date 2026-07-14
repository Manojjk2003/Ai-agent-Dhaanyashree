from pydantic import BaseModel, Field


class BusinessProfile(BaseModel):
    business_name: str = Field(..., min_length=1)
    industry: str = Field(..., min_length=1)
    description: str = ""
    target_audience: list[str] = Field(default_factory=list)
    brand_tone: str = ""
    goals: list[str] = Field(default_factory=list)


class BusinessProfileResponse(BusinessProfile):
    business_id: str
    owner_user_id: str
    updated: bool = True
