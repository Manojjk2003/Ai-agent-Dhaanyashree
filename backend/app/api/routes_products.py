from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.firebase_service import FirebaseService, get_firebase_service


router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ProductResponse:
    return firebase_service.create_product(user, product)


@router.get("", response_model=list[ProductResponse])
def list_products(
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> list[ProductResponse]:
    return firebase_service.list_products(user)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ProductResponse:
    return firebase_service.get_product(user, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product: ProductUpdate,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> ProductResponse:
    return firebase_service.update_product(user, product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> Response:
    firebase_service.delete_product(user, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
