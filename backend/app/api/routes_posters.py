from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.generated_poster import GeneratedPosterCreate, GeneratedPosterResponse
from app.services.firebase_service import FirebaseService, get_firebase_service
from app.services.image_service import VisualAssetContext, generate_poster_image


router = APIRouter(prefix="/posters", tags=["posters"])


@router.get("", response_model=list[GeneratedPosterResponse])
def list_generated_posters(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> list[GeneratedPosterResponse]:
    return firebase_service.list_generated_posters(user)


@router.post(
    "/generate",
    response_model=GeneratedPosterResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_poster(
    request: GeneratedPosterCreate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> GeneratedPosterResponse:
    generated_post = firebase_service.get_generated_post(user, request.post_id)
    business = firebase_service.get_business_profile(user)
    product = firebase_service.get_product(user, generated_post.product_id)
    reference_images = firebase_service.list_reference_images(user)
    visual_context = VisualAssetContext(
        business=business,
        product=product,
        reference_images=tuple(reference_images),
    )
    poster_image = generate_poster_image(
        generated_post,
        user.uid,
        visual_context=visual_context,
    )
    return firebase_service.create_generated_poster(
        user,
        generated_post,
        poster_image,
    )
