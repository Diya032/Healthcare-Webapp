# FastAPI app entrypoint. Creates FastAPI instance, includes routers. 
# Import FastAPI to create the API application
from fastapi import FastAPI

# Import models and database engine to initialize tables
from .models import models
from app.core.database import engine

# Import routers (we’ll create patient routes later)
from .routers import patients, auth, medicalhistory

# ----------------------------
# Step 1a: Create Database Tables
# ----------------------------
# This line ensures that all tables defined in models.py are created in the database
# `bind=engine` tells SQLAlchemy which database engine to use (SQLite for POC)
# Auto-create tables on startup (safe in dev; migrate in prod)
models.Base.metadata.create_all(bind=engine)

# ----------------------------
# Step 1b: Create FastAPI App Instance
# ----------------------------
# This initializes the FastAPI app
# title/version/description are metadata for Swagger UI documentation
app = FastAPI(
    title="Patient Service API",
    version="1.0",
    description="API for managing patients in healthcare system"
)

# ----------------------------
# Step 1c: Include Routers
# ----------------------------
# We mount the patient router under the path /patients
# All endpoints in patients.py will now be available at /patients/...
app.include_router(
    patients.router,
    tags=["Patients"]
)

app.include_router(
    auth.router,
    tags=["Authentication"]
)

app.include_router(
    medicalhistory.router,
    tags=["Medical History"]
)

# ----------------------------
# Step 1d: Root Endpoint
# ----------------------------
# Simple health check endpoint
# Accessing http://127.0.0.1:8000/ will return this message
@app.get("/")
def root():
    return {"message": "Patient Service API is running"}
