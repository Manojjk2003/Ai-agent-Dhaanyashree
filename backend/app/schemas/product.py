from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = ""
    description: str = ""
    benefits: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)
    price: float | None = Field(default=None, ge=0)
    target_audience: list[str] = Field(default_factory=list)
    image_url: str = ""
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    benefits: list[str] | None = None
    ingredients: list[str] | None = None
    price: float | None = Field(default=None, ge=0)
    target_audience: list[str] | None = None
    image_url: str | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    product_id: str
    business_id: str
