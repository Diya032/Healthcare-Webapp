# Centralized CORS origins

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    """
    Configure CORS dynamically:
    - In development → localhost + ngrok
    - In production → only real frontend domain
    """
    if settings.env.lower() == "development":
        origins = [o.strip() for o in settings.dev_cors.split(",")]
    else:  # production
        origins = [o.strip() for o in settings.prod_cors.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
