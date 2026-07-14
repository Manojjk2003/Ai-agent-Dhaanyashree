from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_agent import router as agent_router
from app.api.routes_auth import router as auth_router
from app.api.routes_business import router as business_router
from app.api.routes_health import router as health_router
from app.api.routes_products import router as products_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Marketing Partner API",
        version="0.1.0",
        description=(
            "Backend API and agent orchestration for the AI Marketing Partner.\n\n"
            "Swagger UI is available at `/docs`. Protected routes require a Firebase ID token. "
            "Use the Authorize button and paste the token without the `Bearer` prefix."
        ),
        swagger_ui_parameters={"persistAuthorization": True},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(business_router)
    app.include_router(products_router)
    app.include_router(agent_router, prefix="/agent", tags=["agent"])

    return app


app = create_app()
