from datetime import UTC, datetime

import firebase_admin
from fastapi import HTTPException, status
from firebase_admin import auth, credentials, firestore

from app.config import settings
from app.schemas.auth import CurrentUser
from app.schemas.business import BusinessProfile, BusinessProfileResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


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
            decoded = auth.verify_id_token(token)
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
        return BusinessProfileResponse(
            business_id=doc.id,
            owner_user_id=data.get("owner_user_id", user.uid),
            business_name=data.get("business_name", ""),
            industry=data.get("industry", ""),
            description=data.get("description", ""),
            target_audience=data.get("target_audience", []),
            brand_tone=data.get("brand_tone", ""),
            goals=data.get("goals", []),
            updated=False,
        )

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
        return db.collection("businesses").document(user.uid).collection("products")

    def _product_from_doc(self, user: CurrentUser, doc) -> ProductResponse:
        data = doc.to_dict() or {}
        return ProductResponse(
            product_id=doc.id,
            business_id=user.uid,
            name=data.get("name", ""),
            category=data.get("category", ""),
            description=data.get("description", ""),
            benefits=data.get("benefits", []),
            ingredients=data.get("ingredients", []),
            price=data.get("price"),
            target_audience=data.get("target_audience", []),
            image_url=data.get("image_url", ""),
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
        docs = self._products_collection(user).order_by("created_at").stream()
        return [self._product_from_doc(user, doc) for doc in docs]

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


firebase_service = FirebaseService()


def get_firebase_service() -> FirebaseService:
    return firebase_service
