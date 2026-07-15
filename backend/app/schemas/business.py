from pydantic import BaseModel, Field


class BrandKit(BaseModel):
    logo_url: str = ""
    avatar_url: str = ""
    primary_color: str = "#1b7b68"
    secondary_color: str = "#d9542b"
    accent_color: str = "#f2c94c"
    font_family: str = "Inter"
    heading_font_family: str = "Inter"
    visual_style: list[str] = Field(default_factory=list)
    brand_keywords: list[str] = Field(default_factory=list)


class BusinessProfile(BaseModel):
    business_name: str = Field(..., min_length=1)
    industry: str = Field(..., min_length=1)
    description: str = ""
    website_url: str = ""
    address: str = ""
    phone_number: str = ""
    email: str = ""
    license_number: str = ""
    target_audience: list[str] = Field(default_factory=list)
    brand_tone: str = ""
    goals: list[str] = Field(default_factory=list)
    brand_kit: BrandKit = Field(default_factory=BrandKit)


class BusinessProfileResponse(BusinessProfile):
    business_id: str
    owner_user_id: str
    updated: bool = True
