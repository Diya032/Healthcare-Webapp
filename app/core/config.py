
# app/core/config.py
"""
Centralized application configuration using Pydantic BaseSettings.
Loads from environment variables, with .env support only in local dev.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
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
    # PROD_CORS_ORIGINS:str = Field(..., description="Comma-separated list of allowed CORS origins in production")

    class Config:
        env_file = ".env"  # local convenience
        env_file_encoding = "utf-8"
        extra = "ignore"   # ignore unexpected env vars


# Singleton settings object, import and use everywhere
settings = Settings()
