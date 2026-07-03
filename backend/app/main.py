"""FastAPI entrypoint for the NguonTin backend."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.profiles import router as profiles_router
from app.core.config import settings
from app.core.db import DatabaseConnectionError, init_db

app = FastAPI(title=settings.app_name, version=settings.app_version)
logger = logging.getLogger(__name__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(profiles_router)


@app.on_event("startup")
def on_startup() -> None:
    try:
        init_db()
    except DatabaseConnectionError as exc:
        logger.exception("Database initialization failed")
        raise


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "NguonTin backend is running",
        "docs_url": "/docs",
        "health_url": "/health",
    }
