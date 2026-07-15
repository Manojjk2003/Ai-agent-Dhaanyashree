from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from app.config import settings
from app.schemas.generated_poster import GeneratedPosterResponse
from app.schemas.scheduled_post import ScheduledPostResponse


@dataclass(frozen=True)
class PublishResult:
    provider: str
    platform_post_id: str
    message: str


class SocialService:
    """Publishing adapter boundary for mock and Meta Graph API publishing."""

    def publish_now(
        self,
        scheduled_post: ScheduledPostResponse,
        poster: GeneratedPosterResponse | None = None,
    ) -> PublishResult:
        if settings.social_provider.lower() == "meta" and self._meta_configured:
            return self._publish_meta(scheduled_post, poster)

        return self._publish_mock(scheduled_post)

    @property
    def _meta_configured(self) -> bool:
        return bool(
            settings.meta_page_access_token
            and (
                settings.meta_instagram_business_account_id
                or settings.meta_page_id
            )
        )

    def _publish_mock(self, scheduled_post: ScheduledPostResponse) -> PublishResult:
        platform = scheduled_post.platforms[0] if scheduled_post.platforms else "social"
        return PublishResult(
            provider="mock",
            platform_post_id=f"mock_{platform}_{uuid4().hex[:12]}",
            message=(
                "Mock publish completed. Set SOCIAL_PROVIDER=meta and Meta "
                "credentials to enable live publishing."
            ),
        )

    def _publish_meta(
        self,
        scheduled_post: ScheduledPostResponse,
        poster: GeneratedPosterResponse | None,
    ) -> PublishResult:
        platforms = [platform.lower() for platform in scheduled_post.platforms]
        if not platforms:
            platforms = ["instagram"]

        caption = _caption_for_platform(scheduled_post)
        image_url = poster.image_url if poster else ""
        published_ids: list[str] = []

        if "instagram" in platforms:
            if not image_url:
                raise ValueError("Instagram publishing requires a generated poster image")
            published_ids.append(
                f"instagram:{self._publish_instagram(image_url, caption)}",
            )

        if "facebook" in platforms:
            published_ids.append(
                f"facebook:{self._publish_facebook(image_url, caption)}",
            )

        if not published_ids:
            raise ValueError(
                f"No supported Meta platforms found in scheduled post: {platforms}",
            )

        return PublishResult(
            provider="meta",
            platform_post_id=",".join(published_ids),
            message="Published through Meta Graph API.",
        )

    def _publish_instagram(self, image_url: str, caption: str) -> str:
        if not settings.meta_instagram_business_account_id:
            raise ValueError("META_INSTAGRAM_BUSINESS_ACCOUNT_ID is not configured")

        container = self._post_graph(
            f"/{settings.meta_instagram_business_account_id}/media",
            {
                "image_url": image_url,
                "caption": caption,
                "access_token": settings.meta_page_access_token or "",
            },
        )
        creation_id = container.get("id")
        if not creation_id:
            raise ValueError(f"Instagram media container response missing id: {container}")

        published = self._post_graph(
            f"/{settings.meta_instagram_business_account_id}/media_publish",
            {
                "creation_id": creation_id,
                "access_token": settings.meta_page_access_token or "",
            },
        )
        post_id = published.get("id")
        if not post_id:
            raise ValueError(f"Instagram publish response missing id: {published}")
        return post_id

    def _publish_facebook(self, image_url: str, caption: str) -> str:
        if not settings.meta_page_id:
            raise ValueError("META_PAGE_ID is not configured")

        if image_url:
            published = self._post_graph(
                f"/{settings.meta_page_id}/photos",
                {
                    "url": image_url,
                    "caption": caption,
                    "access_token": settings.meta_page_access_token or "",
                },
            )
        else:
            published = self._post_graph(
                f"/{settings.meta_page_id}/feed",
                {
                    "message": caption,
                    "access_token": settings.meta_page_access_token or "",
                },
            )

        post_id = published.get("post_id") or published.get("id")
        if not post_id:
            raise ValueError(f"Facebook publish response missing id: {published}")
        return post_id

    def _post_graph(self, path: str, payload: dict[str, str]) -> dict:
        body = urlencode(payload).encode("utf-8")
        request = Request(
            f"https://graph.facebook.com/{settings.meta_graph_api_version}{path}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(request, timeout=60) as response:
            parsed = json.loads(response.read().decode("utf-8"))

        if "error" in parsed:
            message = parsed["error"].get("message", "Meta Graph API error")
            raise ValueError(message)
        return parsed


def _caption_for_platform(scheduled_post: ScheduledPostResponse) -> str:
    hashtags = " ".join(scheduled_post.hashtags)
    return f"{scheduled_post.caption}\n\n{hashtags}".strip()


social_service = SocialService()


def get_social_service() -> SocialService:
    return social_service
