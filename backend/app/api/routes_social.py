from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.scheduled_post import PublishNowRequest, PublishNowResponse
from app.services.firebase_service import FirebaseService, get_firebase_service
from app.services.social_service import SocialService, get_social_service


router = APIRouter(prefix="/social", tags=["social"])


@router.post("/publish-now", response_model=PublishNowResponse)
def publish_now(
    request: PublishNowRequest,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    social_service: SocialService = Depends(get_social_service),
) -> PublishNowResponse:
    scheduled_post = firebase_service.get_scheduled_post(
        user,
        request.scheduled_post_id,
    )
    latest_poster = firebase_service.get_latest_generated_poster_for_post(
        user,
        scheduled_post.post_id,
    )

    try:
        result = social_service.publish_now(scheduled_post, latest_poster)
    except Exception as exc:
        failed_post = firebase_service.mark_scheduled_post_failed(
            user,
            request.scheduled_post_id,
            str(exc),
        )
        return PublishNowResponse(
            scheduled_post=failed_post,
            provider="meta" if settings.social_provider.lower() == "meta" else "mock",
            platform_post_id="",
            message=str(exc),
        )

    published_post = firebase_service.mark_scheduled_post_published(
        user,
        request.scheduled_post_id,
        result.platform_post_id,
    )
    return PublishNowResponse(
        scheduled_post=published_post,
        provider=result.provider,
        platform_post_id=result.platform_post_id,
        message=result.message,
    )
