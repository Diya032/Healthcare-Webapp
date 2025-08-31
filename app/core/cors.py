# Centralized CORS origins

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import os
from app.core.config import settings
ENVIRONMENT = settings.ENVIRONMENT

def setup_cors(app):
    """
    Configure CORS dynamically:
    - In development → localhost + ngrok
    - In production → only real frontend domain
    """
    if ENVIRONMENT == "development":
        origins = [o.strip() for o in getattr(settings, "DEV_CORS_ORIGINS", "*").split(",") if o.strip()] + ["null"]
    else:  # production
        origins = [o.strip() for o in getattr(settings, "PROD_CORS_ORIGINS", "*").split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
