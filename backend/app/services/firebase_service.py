from datetime import UTC, datetime

import firebase_admin
from fastapi import HTTPException, status
from firebase_admin import auth, credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.config import settings
from app.schemas.auth import CurrentUser
from app.schemas.business import BrandKit, BusinessProfile, BusinessProfileResponse
from app.schemas.generated_post import (
    GeneratedPostCreate,
    GeneratedPostResponse,
    GeneratedPostUpdate,
)
from app.schemas.generated_poster import GeneratedPosterResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.reference_image import (
    ReferenceImageCreate,
    ReferenceImageResponse,
    ReferenceImageUpdate,
)
from app.schemas.scheduled_post import ScheduledPostCreate, ScheduledPostResponse
from app.services.image_service import PosterImage


def _list_or_empty(value) -> list:
    return value if isinstance(value, list) else []


def _brand_kit_or_default(value) -> BrandKit:
    if isinstance(value, dict):
        return BrandKit(**value)
    return BrandKit()


class FirebaseService:
    def __init__(self) -> None:
        self._app = None
        self._db = None

    def _ensure_app(self):
        if self._app:
            return self._app

        if not settings.firebase_admin_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase Admin is not configured on the backend",
            )

        if settings.firebase_service_account_file:
            certificate = credentials.Certificate(settings.firebase_service_account_file)
        else:
            private_key = settings.firebase_private_key or ""
            normalized_key = private_key.replace("\\n", "\n")

            certificate = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": settings.firebase_project_id,
                    "private_key": normalized_key,
                    "client_email": settings.firebase_client_email,
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            )

        if firebase_admin._apps:
            self._app = firebase_admin.get_app()
        else:
            self._app = firebase_admin.initialize_app(
                certificate,
                {"storageBucket": settings.firebase_storage_bucket},
            )

        return self._app

    def _ensure_db(self):
        if self._db:
            return self._db

        self._ensure_app()
        self._db = firestore.client()
        return self._db

    def verify_id_token(self, token: str) -> CurrentUser:
        self._ensure_app()

        try:
            decoded = auth.verify_id_token(
                token,
                clock_skew_seconds=settings.firebase_token_clock_skew_seconds,
            )
        except Exception as exc:
            detail = "Invalid Firebase token"
            if settings.app_env == "development":
                detail = f"{detail}: {exc}"
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail,
            ) from exc

        return CurrentUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            name=decoded.get("name"),
        )

    def get_business_profile(self, user: CurrentUser) -> BusinessProfileResponse | None:
        db = self._ensure_db()
        doc = db.collection("businesses").document(user.uid).get()

        if not doc.exists:
            return None

        data = doc.to_dict() or {}
        response = BusinessProfileResponse(
            business_id=doc.id,
            owner_user_id=data.get("owner_user_id", user.uid),
            business_name=data.get("business_name", ""),
            industry=data.get("industry", ""),
            description=data.get("description", ""),
            website_url=data.get("website_url", ""),
            address=data.get("address", ""),
            phone_number=data.get("phone_number", ""),
            email=data.get("email", ""),
            license_number=data.get("license_number", ""),
            target_audience=_list_or_empty(data.get("target_audience")),
            brand_tone=data.get("brand_tone", ""),
            goals=_list_or_empty(data.get("goals")),
            brand_kit=_brand_kit_or_default(data.get("brand_kit")),
            updated=False,
        )
        normalized_payload = response.model_dump(exclude={"business_id", "updated"})
        if any(field not in data for field in normalized_payload):
            db.collection("businesses").document(user.uid).set(
                {
                    **normalized_payload,
                    "updated_at": datetime.now(UTC).isoformat(),
                },
                merge=True,
            )
        return response

    def save_business_profile(
        self,
        user: CurrentUser,
        profile: BusinessProfile,
    ) -> BusinessProfileResponse:
        db = self._ensure_db()
        now = datetime.now(UTC).isoformat()
        payload = {
            **profile.model_dump(),
            "owner_user_id": user.uid,
            "updated_at": now,
        }

        doc_ref = db.collection("businesses").document(user.uid)
        existing = doc_ref.get()
        if not existing.exists:
            payload["created_at"] = now

        doc_ref.set(payload, merge=True)

        return BusinessProfileResponse(
            business_id=user.uid,
            owner_user_id=user.uid,
            updated=True,
            **profile.model_dump(),
        )

    def _products_collection(self, user: CurrentUser):
        db = self._ensure_db()
        return db.collection("products")

    def _product_from_doc(self, user: CurrentUser, doc) -> ProductResponse:
        data = doc.to_dict() or {}
        if data.get("business_id") != user.uid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        image_urls = _list_or_empty(data.get("image_urls"))
        image_url = data.get("image_url", "")
        if not image_urls and image_url:
            image_urls = [image_url]

        return ProductResponse(
            product_id=doc.id,
            business_id=data.get("business_id", user.uid),
            name=data.get("name", ""),
            category=data.get("category", ""),
            description=data.get("description", ""),
            benefits=_list_or_empty(data.get("benefits")),
            ingredients=_list_or_empty(data.get("ingredients")),
            price=data.get("price"),
            target_audience=_list_or_empty(data.get("target_audience")),
            image_url=image_url,
            image_urls=image_urls,
            image_notes=data.get("image_notes", ""),
            is_active=data.get("is_active", True),
        )

    def create_product(
        self,
        user: CurrentUser,
        product: ProductCreate,
    ) -> ProductResponse:
        now = datetime.now(UTC).isoformat()
        payload = {
            **product.model_dump(),
            "business_id": user.uid,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = self._products_collection(user).document()
        doc_ref.set(payload)
        return ProductResponse(
            product_id=doc_ref.id,
            business_id=user.uid,
            **product.model_dump(),
        )

    def list_products(self, user: CurrentUser) -> list[ProductResponse]:
        docs = (
            self._products_collection(user)
            .where(filter=FieldFilter("business_id", "==", user.uid))
            .stream()
        )
        products = [self._product_from_doc(user, doc) for doc in docs]
        return sorted(products, key=lambda product: product.name.lower())

    def get_product(self, user: CurrentUser, product_id: str) -> ProductResponse:
        doc = self._products_collection(user).document(product_id).get()

        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return self._product_from_doc(user, doc)

    def update_product(
        self,
        user: CurrentUser,
        product_id: str,
        product: ProductUpdate,
    ) -> ProductResponse:
        doc_ref = self._products_collection(user).document(product_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        payload = product.model_dump(exclude_unset=True)
        payload["updated_at"] = datetime.now(UTC).isoformat()
        doc_ref.set(payload, merge=True)
        return self.get_product(user, product_id)

    def delete_product(self, user: CurrentUser, product_id: str) -> None:
        doc_ref = self._products_collection(user).document(product_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        doc_ref.delete()

    def _reference_images_collection(self, user: CurrentUser):
        db = self._ensure_db()
        return db.collection("reference_images")

    def _reference_image_from_doc(self, user: CurrentUser, doc) -> ReferenceImageResponse:
        data = doc.to_dict() or {}
        if data.get("business_id") != user.uid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference image not found",
            )

        return ReferenceImageResponse(
            reference_image_id=doc.id,
            business_id=data.get("business_id", user.uid),
            name=data.get("name", ""),
            image_url=data.get("image_url", ""),
            reference_type=data.get("reference_type", "ingredient"),
            labels=data.get("labels", []),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def create_reference_image(
        self,
        user: CurrentUser,
        reference_image: ReferenceImageCreate,
    ) -> ReferenceImageResponse:
        now = datetime.now(UTC).isoformat()
        payload = {
            **reference_image.model_dump(),
            "business_id": user.uid,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref = self._reference_images_collection(user).document()
        doc_ref.set(payload)
        return self._reference_image_from_doc(user, doc_ref.get())

    def list_reference_images(self, user: CurrentUser) -> list[ReferenceImageResponse]:
        docs = (
            self._reference_images_collection(user)
            .where(filter=FieldFilter("business_id", "==", user.uid))
            .stream()
        )
        reference_images = [self._reference_image_from_doc(user, doc) for doc in docs]
        return sorted(reference_images, key=lambda item: item.name.lower())

    def update_reference_image(
        self,
        user: CurrentUser,
        reference_image_id: str,
        reference_image: ReferenceImageUpdate,
    ) -> ReferenceImageResponse:
        doc_ref = self._reference_images_collection(user).document(reference_image_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference image not found",
            )

        self._reference_image_from_doc(user, existing)
        payload = reference_image.model_dump(exclude_unset=True)
        payload["updated_at"] = datetime.now(UTC).isoformat()
        doc_ref.set(payload, merge=True)
        return self._reference_image_from_doc(user, doc_ref.get())

    def delete_reference_image(self, user: CurrentUser, reference_image_id: str) -> None:
        doc_ref = self._reference_images_collection(user).document(reference_image_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference image not found",
            )

        self._reference_image_from_doc(user, existing)
        doc_ref.delete()

    def _generated_posts_collection(self, user: CurrentUser):
        db = self._ensure_db()
        return db.collection("generated_posts")

    def _generated_post_from_doc(self, user: CurrentUser, doc) -> GeneratedPostResponse:
        data = doc.to_dict() or {}
        if data.get("business_id") != user.uid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated post not found",
            )

        return GeneratedPostResponse(
            post_id=doc.id,
            business_id=data.get("business_id", user.uid),
            run_id=data.get("run_id", ""),
            content_plan_id=data.get("content_plan_id", ""),
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            selection_reason=data.get("selection_reason", ""),
            content_type=data.get("content_type", ""),
            content_idea=data.get("content_idea", ""),
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", []),
            poster_prompt=data.get("poster_prompt"),
            platforms=data.get("platforms", []),
            run_date=data.get("run_date", ""),
            status=data.get("status", "draft"),
            generation_source=data.get("generation_source", "fallback"),
            scheduled_post_id=data.get("scheduled_post_id"),
            scheduled_at=data.get("scheduled_at"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def create_generated_post(
        self,
        user: CurrentUser,
        post: GeneratedPostCreate,
        post_id: str | None = None,
    ) -> GeneratedPostResponse:
        now = datetime.now(UTC).isoformat()
        payload = {
            **post.model_dump(mode="json"),
            "business_id": user.uid,
            "created_at": now,
            "updated_at": now,
        }

        collection = self._generated_posts_collection(user)
        doc_ref = collection.document(post_id) if post_id else collection.document()
        doc_ref.set(payload)
        return self._generated_post_from_doc(user, doc_ref.get())

    def list_generated_posts(self, user: CurrentUser) -> list[GeneratedPostResponse]:
        docs = (
            self._generated_posts_collection(user)
            .where(filter=FieldFilter("business_id", "==", user.uid))
            .stream()
        )
        posts = [self._generated_post_from_doc(user, doc) for doc in docs]
        return sorted(posts, key=lambda post: post.created_at, reverse=True)

    def get_generated_post(
        self,
        user: CurrentUser,
        post_id: str,
    ) -> GeneratedPostResponse:
        doc = self._generated_posts_collection(user).document(post_id).get()

        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated post not found",
            )

        return self._generated_post_from_doc(user, doc)

    def update_generated_post(
        self,
        user: CurrentUser,
        post_id: str,
        post: GeneratedPostUpdate,
    ) -> GeneratedPostResponse:
        doc_ref = self._generated_posts_collection(user).document(post_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated post not found",
            )

        payload = post.model_dump(exclude_unset=True)
        payload["updated_at"] = datetime.now(UTC).isoformat()
        doc_ref.set(payload, merge=True)
        return self.get_generated_post(user, post_id)

    def delete_generated_post(self, user: CurrentUser, post_id: str) -> None:
        doc_ref = self._generated_posts_collection(user).document(post_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated post not found",
            )

        self._generated_post_from_doc(user, existing)
        doc_ref.delete()

    def _generated_posters_collection(self, user: CurrentUser):
        db = self._ensure_db()
        return db.collection("generated_posters")

    def _generated_poster_from_doc(
        self,
        user: CurrentUser,
        doc,
    ) -> GeneratedPosterResponse:
        data = doc.to_dict() or {}
        if data.get("business_id") != user.uid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated poster not found",
            )

        return GeneratedPosterResponse(
            poster_id=doc.id,
            business_id=data.get("business_id", user.uid),
            post_id=data.get("post_id", ""),
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            prompt=data.get("prompt", ""),
            image_url=data.get("image_url", ""),
            storage_path=data.get("storage_path", ""),
            mime_type=data.get("mime_type", ""),
            provider=data.get("provider", "fallback"),
            error_message=data.get("error_message"),
            status=data.get("status", "generated"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def list_generated_posters(self, user: CurrentUser) -> list[GeneratedPosterResponse]:
        docs = (
            self._generated_posters_collection(user)
            .where(filter=FieldFilter("business_id", "==", user.uid))
            .stream()
        )
        posters = [self._generated_poster_from_doc(user, doc) for doc in docs]
        return sorted(posters, key=lambda poster: poster.created_at, reverse=True)

    def get_latest_generated_poster_for_post(
        self,
        user: CurrentUser,
        post_id: str,
    ) -> GeneratedPosterResponse | None:
        posters = [
            poster
            for poster in self.list_generated_posters(user)
            if poster.post_id == post_id
        ]
        return posters[0] if posters else None

    def create_generated_poster(
        self,
        user: CurrentUser,
        generated_post: GeneratedPostResponse,
        poster_image: PosterImage,
    ) -> GeneratedPosterResponse:
        now = datetime.now(UTC).isoformat()
        payload = {
            "business_id": user.uid,
            "post_id": generated_post.post_id,
            "product_id": generated_post.product_id,
            "product_name": generated_post.product_name,
            "prompt": generated_post.poster_prompt or generated_post.caption,
            "image_url": poster_image.image_url,
            "storage_path": poster_image.storage_path,
            "mime_type": poster_image.mime_type,
            "provider": poster_image.provider,
            "error_message": poster_image.error_message,
            "status": "generated",
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = self._generated_posters_collection(user).document()
        doc_ref.set(payload)
        return self._generated_poster_from_doc(user, doc_ref.get())

    def _scheduled_posts_collection(self, user: CurrentUser):
        db = self._ensure_db()
        return db.collection("scheduled_posts")

    def _scheduled_post_from_doc(self, user: CurrentUser, doc) -> ScheduledPostResponse:
        data = doc.to_dict() or {}
        if data.get("business_id") != user.uid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found",
            )

        return ScheduledPostResponse(
            scheduled_post_id=doc.id,
            business_id=data.get("business_id", user.uid),
            post_id=data.get("post_id", ""),
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            content_type=data.get("content_type", ""),
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", []),
            poster_prompt=data.get("poster_prompt"),
            platforms=data.get("platforms", []),
            scheduled_at=data.get("scheduled_at", ""),
            published_at=data.get("published_at"),
            platform_post_id=data.get("platform_post_id"),
            error_message=data.get("error_message"),
            status=data.get("status", "scheduled"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def list_scheduled_posts(self, user: CurrentUser) -> list[ScheduledPostResponse]:
        docs = (
            self._scheduled_posts_collection(user)
            .where(filter=FieldFilter("business_id", "==", user.uid))
            .stream()
        )
        scheduled_posts = [self._scheduled_post_from_doc(user, doc) for doc in docs]
        return sorted(
            scheduled_posts,
            key=lambda scheduled_post: scheduled_post.scheduled_at,
        )

    def get_scheduled_post(
        self,
        user: CurrentUser,
        scheduled_post_id: str,
    ) -> ScheduledPostResponse:
        doc = self._scheduled_posts_collection(user).document(scheduled_post_id).get()

        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found",
            )

        return self._scheduled_post_from_doc(user, doc)

    def create_scheduled_post(
        self,
        user: CurrentUser,
        scheduled_post: ScheduledPostCreate,
    ) -> ScheduledPostResponse:
        generated_post = self.get_generated_post(user, scheduled_post.post_id)
        if generated_post.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approve generated content before scheduling it",
            )

        now = datetime.now(UTC).isoformat()
        scheduled_at = scheduled_post.scheduled_at.isoformat()
        payload = {
            "business_id": user.uid,
            "post_id": generated_post.post_id,
            "product_id": generated_post.product_id,
            "product_name": generated_post.product_name,
            "content_type": generated_post.content_type,
            "caption": generated_post.caption,
            "hashtags": generated_post.hashtags,
            "poster_prompt": generated_post.poster_prompt,
            "platforms": scheduled_post.platforms,
            "scheduled_at": scheduled_at,
            "status": "scheduled",
            "published_at": None,
            "platform_post_id": None,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        }

        doc_ref = self._scheduled_posts_collection(user).document()
        doc_ref.set(payload)

        self._generated_posts_collection(user).document(generated_post.post_id).set(
            {
                "status": "scheduled",
                "scheduled_post_id": doc_ref.id,
                "scheduled_at": scheduled_at,
                "updated_at": now,
            },
            merge=True,
        )

        return self._scheduled_post_from_doc(user, doc_ref.get())

    def delete_scheduled_post(self, user: CurrentUser, scheduled_post_id: str) -> None:
        doc_ref = self._scheduled_posts_collection(user).document(scheduled_post_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found",
            )

        scheduled_post = self._scheduled_post_from_doc(user, existing)
        if scheduled_post.status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled posts can be cancelled",
            )

        doc_ref.delete()

        generated_doc_ref = self._generated_posts_collection(user).document(
            scheduled_post.post_id,
        )
        generated_doc = generated_doc_ref.get()
        if generated_doc.exists:
            generated_data = generated_doc.to_dict() or {}
            if generated_data.get("business_id") == user.uid:
                generated_doc_ref.set(
                    {
                        "status": "approved",
                        "scheduled_post_id": firestore.DELETE_FIELD,
                        "scheduled_at": firestore.DELETE_FIELD,
                        "updated_at": datetime.now(UTC).isoformat(),
                    },
                    merge=True,
                )

    def mark_scheduled_post_published(
        self,
        user: CurrentUser,
        scheduled_post_id: str,
        platform_post_id: str,
    ) -> ScheduledPostResponse:
        doc_ref = self._scheduled_posts_collection(user).document(scheduled_post_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found",
            )

        scheduled_post = self._scheduled_post_from_doc(user, existing)
        if scheduled_post.status == "published":
            return scheduled_post

        if scheduled_post.status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled posts can be published",
            )

        now = datetime.now(UTC).isoformat()
        doc_ref.set(
            {
                "status": "published",
                "published_at": now,
                "platform_post_id": platform_post_id,
                "error_message": None,
                "updated_at": now,
            },
            merge=True,
        )

        generated_doc_ref = self._generated_posts_collection(user).document(
            scheduled_post.post_id,
        )
        generated_doc = generated_doc_ref.get()
        if generated_doc.exists:
            generated_data = generated_doc.to_dict() or {}
            if generated_data.get("business_id") == user.uid:
                generated_doc_ref.set(
                    {
                        "status": "published",
                        "updated_at": now,
                    },
                    merge=True,
                )

        return self._scheduled_post_from_doc(user, doc_ref.get())

    def mark_scheduled_post_failed(
        self,
        user: CurrentUser,
        scheduled_post_id: str,
        error_message: str,
    ) -> ScheduledPostResponse:
        doc_ref = self._scheduled_posts_collection(user).document(scheduled_post_id)
        existing = doc_ref.get()

        if not existing.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled post not found",
            )

        scheduled_post = self._scheduled_post_from_doc(user, existing)
        if scheduled_post.status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled posts can be marked failed",
            )

        now = datetime.now(UTC).isoformat()
        doc_ref.set(
            {
                "status": "failed",
                "error_message": error_message,
                "updated_at": now,
            },
            merge=True,
        )
        return self._scheduled_post_from_doc(user, doc_ref.get())


firebase_service = FirebaseService()


def get_firebase_service() -> FirebaseService:
    return firebase_service
