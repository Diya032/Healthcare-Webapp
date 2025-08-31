
# app/core/config.py
"""
Centralized application configuration using Pydantic BaseSettings.
Loads from environment variables, with .env support only in local dev.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import logging
# from urllib.parse import quote_plus


# Only load .env in local/dev environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT == "development":
    from dotenv import load_dotenv
    load_dotenv()

# App Settings
#-----------------------------
class Settings(BaseSettings):
    # -------------------
    # Database
    # -------------------
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # -------------------
    # Azure Communication Service
    # -------------------
    ACS_CONNECTION_STRING: str = Field(..., description="Azure Communication Services connection string")
    ACS_SENDER_EMAIL: str = Field(..., description="ACS verified sender email")

    # -------------------
    # JWT Auth
    # -------------------
    SECRET_KEY: str = Field(
        ...,
        description="Secret key used to sign JWTs (HS256). Replace in production!")

    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token lifetime (minutes)")

    # Optional fields for B2C later
    JWT_ISSUER: Optional[str] = None
    JWT_AUDIENCE: Optional[str] = None

    # -------------------
    # CORS
    # -------------------
    DEV_CORS_ORIGINS: str = Field("*, null", description="Comma-separated list of allpwed CORS origins in development")
    PROD_CORS_ORIGINS:str = Field("*", description="Comma-separated list of allowed CORS origins in production")

    # ENV
    ENVIRONMENT: str = Field(ENVIRONMENT, description="Environment: development or production")

    class Config:
        env_file = ".env"  # local convenience
        env_file_encoding = "utf-8"
        extra = "ignore"   # ignore unexpected env vars


# Singleton settings object, import and use everywhere
# settings = Settings()

# -------------------
# Lazy-loaded singleton
# -------------------
# configure logging (if not already configured)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class _LazySettings:
    _settings: Optional[Settings] = None

    def __getattr__(self, name):
        if self._settings is None:
            self._settings = Settings()
            # Log key environment/config values once
            logger.info(f"[Settings] ENVIRONMENT={self._settings.ENVIRONMENT}")
            logger.info(f"[Settings] DEV_CORS_ORIGINS={self._settings.DEV_CORS_ORIGINS}")
            logger.info(f"[Settings] PROD_CORS_ORIGINS={self._settings.PROD_CORS_ORIGINS}")
            logger.info(f"[Settings] DATABASE_URL={self._settings.DATABASE_URL}")

            # optionally log masked or presence info for sensitive keys
            logger.info(f"[Settings] ACS_CONNECTION_STRING is set: {bool(self._settings.ACS_CONNECTION_STRING)}")
            logger.info(f"[Settings] SECRET_KEY is set: {bool(self._settings.SECRET_KEY)}")
        return getattr(self._settings, name)


settings = _LazySettings()