from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.schemas.scheduled_post import ScheduledPostResponse


@dataclass(frozen=True)
class PublishResult:
    provider: str
    platform_post_id: str
    message: str


class SocialService:
    """Publishing adapter boundary.

    The MVP uses a mock adapter so the review/schedule/publish workflow can be
    tested without posting to real social accounts. Meta publishing can replace
    this method without changing the API contract.
    """

    def publish_now(self, scheduled_post: ScheduledPostResponse) -> PublishResult:
        platform = scheduled_post.platforms[0] if scheduled_post.platforms else "social"
        return PublishResult(
            provider="mock",
            platform_post_id=f"mock_{platform}_{uuid4().hex[:12]}",
            message=(
                "Mock publish completed. Connect a real social account before "
                "enabling live publishing."
            ),
        )


social_service = SocialService()


def get_social_service() -> SocialService:
    return social_service
