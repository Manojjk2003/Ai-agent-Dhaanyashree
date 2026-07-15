from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.dependencies import get_current_user
from app.schemas.asset import AssetType, AssetUploadResponse
from app.schemas.auth import CurrentUser
from app.services.storage_service import upload_file_to_storage


router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/upload", response_model=AssetUploadResponse)
def upload_asset(
    asset_type: AssetType = Form(...),
    owner_id: str | None = Form(default=None),
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
) -> AssetUploadResponse:
    folder_by_type = {
        "brand_logo": "brand-assets",
        "brand_avatar": "brand-assets",
        "reference_image": "reference-images",
        "product_image": "product-images",
        "generated_poster": "posters",
    }
    prefix_by_type = {
        "brand_logo": "logo",
        "brand_avatar": "avatar",
        "reference_image": owner_id,
        "product_image": owner_id,
        "generated_poster": owner_id,
    }
    owner_folder = prefix_by_type[asset_type] or None
    asset = upload_file_to_storage(
        file=file,
        business_id=user.uid,
        folder=folder_by_type[asset_type],
        owner_id=owner_folder,
    )
    return AssetUploadResponse(
        image_url=asset.image_url,
        storage_path=asset.storage_path,
        content_type=asset.content_type,
        file_name=asset.file_name,
    )
