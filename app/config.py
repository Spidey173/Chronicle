"""Application configuration using Pydantic Settings."""

import json
import os
from pathlib import Path
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Platform settings with environment variable overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core
    APP_NAME: str = "Chronicle"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (uses /tmp on serverless environments like Vercel if no external DB provided)
    DATABASE_URL: str = Field(
        default_factory=lambda: "sqlite:////tmp/analytics.db" if os.environ.get("VERCEL") else "sqlite:///./data/analytics.db"
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # JWT Authentication
    SECRET_KEY: str = "super-secret-jwt-key-change-in-production-min-32-chars-long!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Initial Admin Seed
    INITIAL_ADMIN_EMAIL: str = "admin@example.com"
    INITIAL_ADMIN_PASSWORD: str = "AdminSecurePassword123!"
    INITIAL_ADMIN_NAME: str = "System Administrator"

    # Ingestion & Storage Directories
    UPLOAD_DIR: Path = Field(
        default_factory=lambda: Path("/tmp/storage/uploads") if os.environ.get("VERCEL") else Path("./storage/uploads")
    )
    QUARANTINE_DIR: Path = Field(
        default_factory=lambda: Path("/tmp/storage/quarantine") if os.environ.get("VERCEL") else Path("./storage/quarantine")
    )
    MAX_UPLOAD_SIZE_MB: int = 50

    # Currency exchange rates relative to USD (1.0)
    CURRENCY_RATES_JSON: str = '{"USD": 1.0, "EUR": 1.08, "GBP": 1.28, "CAD": 0.73, "INR": 0.012, "AUD": 0.66}'

    # AWS S3 Settings (optional)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = ""
    USE_S3_STORAGE: bool = False

    @property
    def currency_rates(self) -> Dict[str, float]:
        """Parse currency conversion rates from JSON."""
        try:
            return json.loads(self.CURRENCY_RATES_JSON)
        except Exception:
            return {"USD": 1.0, "EUR": 1.08, "GBP": 1.28, "CAD": 0.73, "INR": 0.012, "AUD": 0.66}

    def ensure_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        try:
            self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            self.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
            if not os.environ.get("VERCEL"):
                Path("./data").mkdir(parents=True, exist_ok=True)
        except OSError:
            pass


settings = Settings()
settings.ensure_directories()
