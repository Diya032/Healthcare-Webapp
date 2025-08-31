# Centralized CORS origins
# app/core/cors.py
# Centralized CORS origins

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

def setup_cors(app):
    """
    Configure CORS dynamically:
    - In development → localhost + ngrok
    - In production → only real frontend domain
    """
    try:
        environment = settings.ENVIRONMENT
        logger.info(f"Setting up CORS for environment: {environment}")
        
        # Safe attribute access with fallback to environment variables
        if environment == "development":
            try:
                origins_str = settings.DEV_CORS_ORIGINS
            except AttributeError:
                origins_str = os.getenv("DEV_CORS_ORIGINS", "*, null")
                logger.warning(f"Fallback to env var DEV_CORS_ORIGINS: {origins_str}")
        else:  # production
            try:
                origins_str = settings.PROD_CORS_ORIGINS
            except AttributeError:
                origins_str = os.getenv("PROD_CORS_ORIGINS", "*")
                logger.warning(f"Fallback to env var PROD_CORS_ORIGINS: {origins_str}")
        
        logger.info(f"CORS origins string: {origins_str}")
        
        # Parse origins
        if origins_str == "*":
            origins = ["*"]
        else:
            origins = [o.strip() for o in origins_str.split(",") if o.strip()]
            if environment == "development" and "null" not in origins:
                origins.append("null")  # Add null for development
        
        logger.info(f"Final CORS origins: {origins}")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        logger.info("CORS middleware configured successfully")
        
    except Exception as e:
        logger.error(f"CORS configuration error: {e}")
        logger.error(f"Environment: {environment}")
        logger.error(f"Available env vars: {[k for k in os.environ.keys() if 'CORS' in k]}")
        
        # Fallback CORS setup
        logger.warning("Using fallback CORS configuration")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    return app