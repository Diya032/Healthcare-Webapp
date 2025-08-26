# Centralized CORS origins

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import os
ENVIRONMENT = os.getenv("ENVIRONMENT").lower()

def setup_cors(app):
    """
    Configure CORS dynamically:
    - In development → localhost + ngrok
    - In production → only real frontend domain
    """
    if ENVIRONMENT == "development":
        origins = [o.strip() for o in settings.DEV_CORS_ORIGINS.split(",")] + ["null"]
    else:  # production
        origins = [o.strip() for o in settings.PROD_CORS_ORIGINS.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
