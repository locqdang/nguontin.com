"""FastAPI entrypoint for the NguonTin backend."""

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.db import init_db

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(auth_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "NguonTin backend is running",
        "docs_url": "/docs",
        "health_url": "/health",
    }
