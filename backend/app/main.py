from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_agent import router as agent_router
from app.api.routes_health import router as health_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Marketing Partner API",
        version="0.1.0",
        description="Backend API and agent orchestration for the AI Marketing Partner.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(agent_router, prefix="/agent", tags=["agent"])

    return app


app = create_app()
