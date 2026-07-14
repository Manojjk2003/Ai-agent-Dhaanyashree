from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import CurrentUser
from app.services.firebase_service import FirebaseService, get_firebase_service


bearer_scheme = HTTPBearer(
    scheme_name="Firebase ID token",
    description="Paste a Firebase ID token. Swagger will send it as Authorization: Bearer <token>.",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> CurrentUser:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Firebase bearer token",
        )

    return firebase_service.verify_id_token(credentials.credentials)
