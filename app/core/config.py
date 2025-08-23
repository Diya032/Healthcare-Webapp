# app/core/config.py
"""
Application configuration using Pydantic BaseSettings.

Centralizes DB URL, JWT settings, and CORS origins.
Development uses ngrok for remote frontend access.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # ----------------------------
    # Database
    # ----------------------------
    DATABASE_URL: str = Field(
        default="sqlite:///./patients.db",
        description="Database connection URL (SQLAlchemy format)."
    )

    # ----------------------------
    # JWT / Authentication
    # ----------------------------
    SECRET_KEY: str = Field(
        default="change-me-in-prod-very-secret-and-long-string",
        description="Secret key used to sign JWTs (HS256). Replace in prod."
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token lifetime (minutes)")
    JWT_ISSUER: Optional[str] = Field(default=None, description="Optional JWT issuer claim")
    JWT_AUDIENCE: Optional[str] = Field(default=None, description="Optional JWT audience claim")

    # ----------------------------
    # Environment & CORS
    # ----------------------------
    env: str = Field(default="development", description="Current environment: development or production")
    dev_cors: str = Field(
        default= "https://ab37c26da88c.ngrok-free.app",
        description="Dev CORS origins (ngrok URL for remote frontend)"
    )
    prod_cors: str = Field(
        default="https://myfrontend.com",
        description="Prod CORS origins (your real frontend domain)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# singleton settings object to import across the app
settings = Settings()
