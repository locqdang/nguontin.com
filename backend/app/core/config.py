"""Application configuration for the NguonTin backend."""
import os
from pathlib import Path

from dotenv import load_dotenv


def _split_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "nguontin.db"

load_dotenv(BASE_DIR.parent / ".env", override=False)
load_dotenv(BASE_DIR.parent / ".env.local", override=True)


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "NguonTin API")
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_version = os.getenv("APP_VERSION", "0.1.0")
        self.database_path = os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))
        self.jwt_secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
        self.email_login_code_ttl_minutes = int(os.getenv("EMAIL_LOGIN_CODE_TTL_MINUTES", "15"))
        self.email_delivery_timeout_seconds = int(os.getenv("EMAIL_DELIVERY_TIMEOUT_SECONDS", "10"))
        self.oauth_http_timeout_seconds = int(os.getenv("OAUTH_HTTP_TIMEOUT_SECONDS", "10"))
        self.n8n_email_login_webhook_url = os.getenv("N8N_EMAIL_LOGIN_WEBHOOK_URL", "").strip()
        self.n8n_email_login_webhook_secret = os.getenv("N8N_EMAIL_LOGIN_WEBHOOK_SECRET", "").strip()
        self.frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:3007")
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        self.google_oauth_redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "").strip()
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
        self.linkedin_oauth_redirect_uri = os.getenv("LINKEDIN_OAUTH_REDIRECT_URI", "").strip()
        cors_allow_origins_raw = os.getenv(
            "CORS_ALLOW_ORIGINS",
            os.getenv("CORS_ALLOW_ORIGIN", f"{self.frontend_base_url},http://127.0.0.1:3001"),
        )
        self.cors_allow_origins = _split_csv_env(cors_allow_origins_raw)

    @property
    def is_dev_secret(self) -> bool:
        return self.jwt_secret == "dev-secret-change-me"


settings = Settings()
