from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.generated_post import GeneratedPostResponse, GeneratedPostUpdate
from app.services.firebase_service import FirebaseService, get_firebase_service


router = APIRouter(prefix="/content", tags=["content"])


@router.get("/posts", response_model=list[GeneratedPostResponse])
def list_generated_posts(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> list[GeneratedPostResponse]:
    return firebase_service.list_generated_posts(user)


@router.get("/posts/{post_id}", response_model=GeneratedPostResponse)
def get_generated_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> GeneratedPostResponse:
    return firebase_service.get_generated_post(user, post_id)


@router.patch("/posts/{post_id}", response_model=GeneratedPostResponse)
def update_generated_post(
    post_id: str,
    post: GeneratedPostUpdate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> GeneratedPostResponse:
    return firebase_service.update_generated_post(user, post_id, post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generated_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> Response:
    firebase_service.delete_generated_post(user, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
