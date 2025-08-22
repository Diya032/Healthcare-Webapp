# app/core/dependencies.py
"""
Auth-related dependencies for FastAPI.

This module defines reusable dependencies for routes that require authentication.
It separates concerns cleanly so that swapping DB auth with Azure AD B2C later
requires minimal changes.

Dependencies provided here:
1. oauth2_scheme: tells FastAPI where clients should provide JWT tokens.
2. get_current_user: decodes token, verifies it, loads the User from DB.
3. get_current_patient_or_409: ensures the current user has an associated Patient.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Any, Dict

from .database import get_db   # DB session dependency
from app.models import models
from app.crud import crud_user, crud
from .security import decode_access_token  # JWT decoding; raises TokenDecodeError

# ----------------------------
# OAuth2 scheme
# ----------------------------
# FastAPI uses this to know where to find the token.
# This also automatically generates Swagger UI docs for protected endpoints.
# `tokenUrl` is relative to the current app: where clients POST their credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ----------------------------
# Custom Exceptions
# ----------------------------
class InvalidTokenError(HTTPException):
    """
    Convenience exception for invalid or missing JWT tokens.
    Returns 401 Unauthorized and sets WWW-Authenticate header.
    """
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ----------------------------
# Dependencies
# ----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Decode the JWT and load the corresponding User from the DB.

    Steps:
    1. decode_access_token(token) -> payload dict or raises TokenDecodeError
    2. Extract 'sub' claim (user_id)
    3. Convert to int if needed
    4. Load user from DB; raise 401 if not found

    Returns:
        models.User instance
    Raises:
        InvalidTokenError (HTTP 401) if token is invalid, missing, or user not found
    """
    from .security import TokenDecodeError  # local import to avoid circular import

    try:
        payload: Dict[str, Any] = decode_access_token(token)
    except TokenDecodeError as exc:
        raise InvalidTokenError(detail=str(exc))

    # Extract user ID from 'sub' claim
    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError(detail="Token payload missing 'sub' claim")

    try:
        user_id = str(user_id)
    except (TypeError, ValueError):
        raise InvalidTokenError(detail="Invalid 'sub' claim in token")

    # Load user from DB
    user = crud_user.get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise InvalidTokenError(detail="User not found")

    return user


def get_current_patient_or_409(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> models.Patient:
    """
    Ensure that the current authenticated user has a Patient profile.

    Returns:
        models.Patient instance
    Raises:
        HTTPException 409 Conflict if no patient exists for the current user

    Notes:
    - This matches the "phase 2/3 contract": user may exist without patient profile.
    - Used in endpoints that require a patient object (appointments, medical history, etc.)
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient profile not created yet for this user",
        )
    return patient
