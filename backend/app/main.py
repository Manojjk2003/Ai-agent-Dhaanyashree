from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_agent import router as agent_router
from app.api.routes_auth import router as auth_router
from app.api.routes_business import router as business_router
from app.api.routes_content import router as content_router
from app.api.routes_health import router as health_router
from app.api.routes_posters import router as posters_router
from app.api.routes_products import router as products_router
from app.api.routes_schedule import router as schedule_router
from app.api.routes_social import router as social_router
from app.config import BACKEND_DIR
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

    poster_static_dir = BACKEND_DIR.parent / "generated" / "posters"
    poster_static_dir.mkdir(parents=True, exist_ok=True)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(business_router)
    app.include_router(products_router)
    app.include_router(content_router)
    app.include_router(schedule_router)
    app.include_router(posters_router)
    app.include_router(social_router)
    app.include_router(agent_router, prefix="/agent", tags=["agent"])
    app.mount(
        "/static/posters",
        StaticFiles(directory=poster_static_dir),
        name="posters",
    )

    return app


app = create_app()
