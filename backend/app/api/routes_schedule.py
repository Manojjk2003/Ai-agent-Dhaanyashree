from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.scheduled_post import (
    ScheduleRecommendationRequest,
    ScheduleRecommendationResponse,
    ScheduledPostCreate,
    ScheduledPostResponse,
)
from app.services.firebase_service import FirebaseService, get_firebase_service
from app.services.llm_service import recommend_schedule_time


router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/posts", response_model=list[ScheduledPostResponse])
def list_scheduled_posts(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> list[ScheduledPostResponse]:
    return firebase_service.list_scheduled_posts(user)


@router.post(
    "/posts",
    response_model=ScheduledPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scheduled_post(
    scheduled_post: ScheduledPostCreate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ScheduledPostResponse:
    return firebase_service.create_scheduled_post(user, scheduled_post)


@router.post("/recommend-time", response_model=ScheduleRecommendationResponse)
def recommend_time(
    request: ScheduleRecommendationRequest,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ScheduleRecommendationResponse:
    business = firebase_service.get_business_profile(user)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create the business profile before recommending a schedule time",
        )

    generated_post = firebase_service.get_generated_post(user, request.post_id)
    product = firebase_service.get_product(user, generated_post.product_id)

    return recommend_schedule_time(
        business=business,
        product=product,
        generated_post=generated_post,
        target_date=request.target_date,
        platforms=request.platforms,
    )


@router.delete("/posts/{scheduled_post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_post(
    scheduled_post_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> Response:
    firebase_service.delete_scheduled_post(user, scheduled_post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
