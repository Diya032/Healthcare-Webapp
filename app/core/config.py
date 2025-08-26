# Config settings. Handles DB URL, env variables, and app config. 
# pydantic settings: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# app/core/config.py
"""
Application configuration using Pydantic BaseSettings.

This centralizes SECRET_KEY, JWT algorithm, and token TTL, and
loads from environment variables (recommended for production).
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from urllib.parse import quote_plus


#-----------------------------
#adding one source of truth of db url
import os
from dotenv import load_dotenv
# load_dotenv()  # take environment variables from .env.

# Only load .env in local/dev environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT == "development":
    load_dotenv()



# ----------------------------
# Database URL builder (handles special chars in password)
# ----------------------------
# user = "healthcare_db_server"
# password = quote_plus(os.getenv("DATABASE_PASSWORD", ""))  # quote_plus handles special characters
# server = "sqlhealthcareserver.database.windows.net"
# database = "healthcare_sql_db"

# Single source of truth for DB URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.abspath('patients.db')}"   # fallback if not set
)

# DATABASE_URL = (
#     f"mssql+pyodbc://{user}:{password}@{server}:1433/{database}"
#     "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
# )
#-----------------------------

#-----------------------------
# App Settings
class Settings(BaseSettings):
    DATABASE_URL: str = Field(default=DATABASE_URL, description="Database connection URL")
    ACS_CONNECTION_STRING: str 
    ACS_SENDER_EMAIL: str 
    # IMPORTANT: In production, set this in environment (DO NOT hardcode)
    SECRET_KEY: str = Field(
        default="change-me-in-prod-very-secret-and-long-string",
        description="Secret key used to sign JWTs (HS256). Replace in prod."
    )

    # JWT algorithm. HS256 is typical for symmetric-signature.
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")

    # Access token TTL in minutes (short-lived tokens). Typical values: 15, 30, 60.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token lifetime (minutes)")

    # Optional issuer/audience may want to validate later (B2C integration).
    JWT_ISSUER: Optional[str] = Field(default=None, description="Optional JWT issuer claim to validate")
    JWT_AUDIENCE: Optional[str] = Field(default=None, description="Optional JWT audience claim to validate")

    class Config:
        env_file = ".env"   # local convenience: read env vars from .env if present
        env_file_encoding = "utf-8"
        extra = "allow"  # ignore other unexpected env vars


# singleton settings object to import across the app
settings = Settings()
