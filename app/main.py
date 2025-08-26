# FastAPI app entrypoint. Creates FastAPI instance, includes routers. 
# Import FastAPI to create the API application
from fastapi import FastAPI, Request
import time

# Import models and database engine to initialize tables
from .models import models
from app.core.database import engine

# Import routers (we’ll create patient routes later)
from .routers import patients, auth, medicalhistory, appointments, admin

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

# Import and set up CORS middleware
from app.core.cors import setup_cors
from app.core.debug_options_cors import OptionsDebugMiddleware
app = setup_cors(app)

# Apply OPTIONS debug middleware next
app.add_middleware(OptionsDebugMiddleware)

# REQUEST LOGGING MIDDLEWARE - logs all requests and responses for debogging purposes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"\n[REQUEST] {request.method} {request.url}")
    print(f"[HEADERS] {dict(request.headers)}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"[RESPONSE] Status: {response.status_code}, Time: {process_time:.2f}s")
    return response

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

app.include_router(
    appointments.router, 
    tags=["Appointments"]
)  # <- appointments added

app.include_router(
    admin.router,
    tags=["Admin"]
) # <- admin added

# ----------------------------
# Step 1d: Root Endpoint
# ----------------------------
# Simple health check endpoint
# Accessing http://127.0.0.1:8000/ will return this message
@app.get("/")
def root():
    return {"message": "Patient Service API is running"}

