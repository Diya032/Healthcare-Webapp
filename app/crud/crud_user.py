# app/crud_user.py
# ------------------------------------------------------
# CRUD operations specifically for User table.
# Keeps auth logic separate from domain-specific Patients.
# ------------------------------------------------------

from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
# from app.core.security import hash_password

# ----------------------------
# CREATE USER
# ----------------------------
def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new User row with hashed password.
    Caller should ensure email uniqueness before calling.
    
    Args:
        db: SQLAlchemy session
        user_in: Pydantic UserCreate schema (email + raw password)
    
    Returns:
        User instance
    """
    db_user = models.User(
        email=user_in.email,
        hashed_password=user_in.password  # store hashed password only auth/signup/ gived hashed pwd only as user_in
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ----------------------------
# GET USER BY EMAIL
# ----------------------------
def get_user_by_email(db: Session, email: str) -> models.User | None:
    """
    Retrieve a User object by email.
    Useful for login/authentication.
    """
    
    return db.query(models.User).filter(models.User.email == email).first()


# ----------------------------
# GET USER BY ID
# ----------------------------
def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """
    Retrieve a User object by primary key.
    Useful for token decoding / current user dependency.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


# ----------------------------
# AUTHENTICATE USER (UNNEEDED DUE TO AUTH BACKEND)
# ----------------------------
# def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
#     """
#     Verify user credentials.
#     - Return User instance if email exists and password matches
#     - Return None otherwise
    
#     Note: Only compares against hashed password.
#     """
#     user = get_user_by_email(db, email)
#     if not user:
#         return None
#     if not verify_password(password, user.hashed_password):
#         return None
#     return user
