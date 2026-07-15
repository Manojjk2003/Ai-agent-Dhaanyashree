from typing import Literal

from pydantic import BaseModel


AssetType = Literal[
    "brand_logo",
    "brand_avatar",
    "reference_image",
    "product_image",
    "generated_poster",
]


class AssetUploadResponse(BaseModel):
    image_url: str
    storage_path: str
    content_type: str
    file_name: str
