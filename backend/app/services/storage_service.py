from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from firebase_admin import storage

from app.config import settings


@dataclass(frozen=True)
class StoredAsset:
    image_url: str
    storage_path: str
    content_type: str
    file_name: str


def upload_file_to_storage(
    file: UploadFile,
    business_id: str,
    folder: str,
    owner_id: str | None = None,
) -> StoredAsset:
    data = file.file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0]
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are supported",
        )

    extension = Path(file.filename or "").suffix
    if not extension:
        extension = mimetypes.guess_extension(content_type) or ".bin"

    safe_owner = f"{owner_id.strip('/')}/" if owner_id else ""
    file_name = f"{uuid4().hex}{extension.lower()}"
    storage_path = f"businesses/{business_id}/{folder}/{safe_owner}{file_name}"
    return upload_bytes_to_storage(data, content_type, storage_path)


def upload_bytes_to_storage(
    data: bytes,
    content_type: str,
    storage_path: str,
) -> StoredAsset:
    if not settings.firebase_storage_bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase Storage bucket is not configured",
        )

    token = uuid4().hex
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    blob.metadata = {"firebaseStorageDownloadTokens": token}
    blob.upload_from_string(data, content_type=content_type)
    blob.patch()

    encoded_path = quote(storage_path, safe="")
    image_url = (
        f"https://firebasestorage.googleapis.com/v0/b/"
        f"{settings.firebase_storage_bucket}/o/{encoded_path}?alt=media&token={token}"
    )
    return StoredAsset(
        image_url=image_url,
        storage_path=storage_path,
        content_type=content_type,
        file_name=Path(storage_path).name,
    )
