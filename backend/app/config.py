from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins_raw: str = "http://localhost:5173"
    backend_public_url: str = "http://localhost:8000"
    llm_provider: str = "mock"
    image_provider: str = "fallback"
    gemini_model: str = "gemini-3.5-flash"
    gemini_image_model: str = "gemini-3.1-flash-image"
    gemini_api_key: str | None = None
    hf_token: str | None = None
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    openrouter_api_key: str | None = None
    groq_api_key: str | None = None
    firebase_project_id: str | None = None
    firebase_client_email: str | None = None
    firebase_private_key: str | None = None
    firebase_storage_bucket: str | None = None
    firebase_service_account_file: str | None = None
    firebase_token_clock_skew_seconds: int = 10
    social_provider: str = "mock"
    meta_graph_api_version: str = "v23.0"
    meta_page_id: str | None = None
    meta_page_access_token: str | None = None
    meta_instagram_business_account_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]

    @property
    def firebase_admin_configured(self) -> bool:
        has_service_file = bool(self.firebase_service_account_file)
        has_inline_credentials = all(
            [
                self.firebase_project_id,
                self.firebase_client_email,
                self.firebase_private_key,
            ]
        )
        return has_service_file or has_inline_credentials


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
