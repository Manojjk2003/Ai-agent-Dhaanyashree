from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import CurrentUser


router = APIRouter(tags=["auth"])


@router.get("/me", response_model=CurrentUser)
def read_current_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
