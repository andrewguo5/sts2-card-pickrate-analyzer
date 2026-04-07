"""
Application configuration.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://localhost:5432/sts2_analytics"

    # Security
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # Server
    host: str = "0.0.0.0"
    port: int = 8000  # Railway will override this with $PORT

    # Upload access code
    upload_access_code: str = "CHANGE_ME_IN_PRODUCTION"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
