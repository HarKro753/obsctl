"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings
from app.db.schema import init_db
from app.routes.auth import router as auth_router
from app.routes.credentials import router as credentials_router
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, close on shutdown."""
    settings: Settings = app.state.settings
    app.state.db = init_db(settings.database_path)
    yield
    app.state.db.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional Settings override (useful for testing).

    Returns:
        Configured FastAPI instance.
    """
    if settings is None:
        settings = Settings()

    app = FastAPI(
        title="obsidian-managed-sync",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.settings = settings

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(credentials_router)

    return app


# Default app instance for `uvicorn app.main:app`
app = create_app()
