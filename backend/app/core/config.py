"""Application configuration for the NguonTin backend."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "nguontin.db"


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "NguonTin API")
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_version = os.getenv("APP_VERSION", "0.1.0")
        self.database_path = os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))
        self.jwt_secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
        self.cors_allow_origin = os.getenv("CORS_ALLOW_ORIGIN", "http://127.0.0.1:3007")

    @property
    def is_dev_secret(self) -> bool:
        return self.jwt_secret == "dev-secret-change-me"


settings = Settings()
