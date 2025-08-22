# app/core/auth_backend.py

# auth strategy (DB now, B2C later)

'''
Right now authenticate ties directly to the database check. 
Later, ehen making switch to Azure AD B2C ,
we want to avoid rewriting whole CRUD layer.

Provides Abstraction layer between auth logic and CRUD operations.

'''

from typing import Protocol, Optional
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas import schemas
from app.models import models
from . import security


class AuthBackend(Protocol):
    """
    Protocol (interface) for authentication backends.

    Any auth backend must implement a `authenticate()` method that takes
    credentials and either returns a valid User/Patient object or None.

    Examples of backends:
    - DatabaseAuthBackend: checks email + password against local DB
    - AzureB2CAuthBackend: validates tokens from Azure AD B2C
    """

    def authenticate(self, db: Session, credentials: schemas.LoginSchema) -> Optional[models.User]:
        ...


class DatabaseAuthBackend:
    """
    Authentication backend for local database users.
    Validates plain email + password against our Patients table.
    """

    def authenticate(self, db: Session, credentials: schemas.LoginSchema) -> Optional[models.User]:
        # Fetch user by email
        user = crud_user.get_user_by_email(db, email=credentials.email)
        # print("Fetched user:", user)
        if not user:
            # print("No user found for email:", credentials.email)
            return None

        # Verify hashed password using security helpers
        # print("Verfifying email for user:", user.email)
        # print("Stored hash:", user.hashed_password)
        # print("Provided password:", credentials.password)
        
        valid, _ = security.verify_password(credentials.password, user.hashed_password)
        # print("Password valid?", valid)
        if not valid:
            return None

        # Return the user if login is valid
        return user


# Placeholder for Azure AD B2C
class AzureB2CAuthBackend:
    """
    Future backend for Azure AD B2C.
    Instead of checking passwords, this would validate a JWT
    from Azure B2C using Microsoft’s public keys.
    """

    def authenticate(self, db: Session, credentials: schemas.LoginSchema) -> Optional[models.User]:
        # Example (not implemented yet):
        # 1. Decode and validate the B2C token
        # 2. Extract email/ID from claims
        # 3. Optionally sync user into our DB if not present
        raise NotImplementedError("Azure B2C authentication not yet implemented.")


# Dispatcher function (used by routers/auth.py)
def authenticate(db: Session, credentials: schemas.LoginSchema, backend: Optional[AuthBackend] = None) -> Optional[models.User]:
    """
    Authenticate a user with the selected backend.
    Default is DatabaseAuthBackend for now.
    """

    if backend is None:
        backend = DatabaseAuthBackend()

    return backend.authenticate(db, credentials)
