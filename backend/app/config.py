from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    DATABASE_URL: Optional[str] = None

    # ---------------------------------------------------------
    # ML Artifacts
    # ---------------------------------------------------------
    SUPPLYPRESCRIPT_MODEL_DIR: Optional[str] = None

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------
    AUTH_ENABLED: bool = False

    # ---------------------------------------------------------
    # Pydantic Settings
    # ---------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings


def get_model_dir() -> Path:
    settings = get_settings()

    if settings.SUPPLYPRESCRIPT_MODEL_DIR:
        return Path(
            settings.SUPPLYPRESCRIPT_MODEL_DIR
        )

    # Default:
    # SupplyPrescript-AI/backend/models
    return (
        Path(__file__)
        .resolve()
        .parent
        .parent
        / "models"
    )