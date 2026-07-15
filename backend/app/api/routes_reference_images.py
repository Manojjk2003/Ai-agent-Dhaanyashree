from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.reference_image import (
    ReferenceImageCreate,
    ReferenceImageResponse,
    ReferenceImageUpdate,
)
from app.services.firebase_service import FirebaseService, get_firebase_service


router = APIRouter(prefix="/reference-images", tags=["reference-images"])


@router.post("", response_model=ReferenceImageResponse, status_code=status.HTTP_201_CREATED)
def create_reference_image(
    reference_image: ReferenceImageCreate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ReferenceImageResponse:
    return firebase_service.create_reference_image(user, reference_image)


@router.get("", response_model=list[ReferenceImageResponse])
def list_reference_images(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> list[ReferenceImageResponse]:
    return firebase_service.list_reference_images(user)


@router.patch("/{reference_image_id}", response_model=ReferenceImageResponse)
def update_reference_image(
    reference_image_id: str,
    reference_image: ReferenceImageUpdate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ReferenceImageResponse:
    return firebase_service.update_reference_image(
        user,
        reference_image_id,
        reference_image,
    )


@router.delete("/{reference_image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reference_image(
    reference_image_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> Response:
    firebase_service.delete_reference_image(user, reference_image_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
