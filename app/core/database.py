from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ----------------------------
# Step 1a: Define Database URL
# ----------------------------
# Using SQLite for local POC; database file will be created automatically
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# If SQLite, need special connect args
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# ----------------------------
# Step 1b: Create Engine
# ----------------------------
# The engine connects SQLAlchemy to the database
# connect_args={"check_same_thread": False} is required only for SQLite
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False}
# )

# ----------------------------
# Step 1c: Create Session
# ----------------------------
# SessionLocal creates a session factory
# This session will be used to interact with the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ----------------------------
# Step 1d: Base class for Models
# ----------------------------
# All ORM models will inherit from this Base
Base = declarative_base()

# ----------------------------
# Step 1e: Dependency to get DB session
# ----------------------------
# FastAPI dependency: endpoints can use `Depends(get_db)` to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db  # provides the session to the endpoint
    finally:
        db.close()  # ensures session is closed after use
