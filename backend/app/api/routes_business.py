from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.business import BusinessProfile, BusinessProfileResponse
from app.services.firebase_service import FirebaseService, get_firebase_service


router = APIRouter(prefix="/business", tags=["business"])


@router.get("/profile", response_model=BusinessProfileResponse | None)
def get_business_profile(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> BusinessProfileResponse | None:
    return firebase_service.get_business_profile(user)


@router.post("/profile", response_model=BusinessProfileResponse)
def save_business_profile(
    profile: BusinessProfile,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> BusinessProfileResponse:
    return firebase_service.save_business_profile(user, profile)
