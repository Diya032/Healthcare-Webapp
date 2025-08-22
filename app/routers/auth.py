# /signup, /login

# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.models import models
from app.core.database import get_db
from app.core import security
from app.core import auth_backend  # <-- our new abstraction layer
from app.crud import crud_user

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/signup", response_model=schemas.UserResponse)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    User signup endpoint.
    - Takes email + password from request body
    - Hashes the password
    - Stores new Patient in the database
    """

    # Check if email is already registered
    existing = db.query(models.User).filter_by(email=user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password before saving
    hashed_password = security.hash_password(user_in.password)

    # Create patient model
    user_data = schemas.UserCreate(
        email=user_in.email,
        password=hashed_password,  # replace plain password with hash
    )

    # Save to DB using crud_user.py
    new_user = crud_user.create_user(db, user_data)

    return new_user


# @router.post("/login")
# def login(credentials: schemas.LoginSchema, db: Session = Depends(get_db)):
#     """
#     User login endpoint.
#     - Calls `auth_backend.authenticate()` with given credentials
#     - On success: returns a JWT token
#     - On failure: raises 401 Unauthorized
#     """

#     user = auth_backend.authenticate(db, credentials)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     # Generate JWT access token
#     access_token = security.create_access_token(data={"sub": str(user.id)})

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#     }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_backend.authenticate(db, schemas.LoginSchema(
        email=form_data.username,
        password=form_data.password
    ))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# # Option 1: Modify existing endpoint to handle OAuth2PasswordRequestForm
# @router.post("/login")
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(), 
#     db: Session = Depends(get_db)
# ):
#     """
#     User login endpoint - OAuth2 compatible.
#     - Accepts form data for Swagger OAuth2 integration
#     - On success: returns a JWT token
#     - On failure: raises 401 Unauthorized
#     """
    
#     # Create credentials object from form data
#     credentials = schemas.LoginSchema(
#         email=form_data.username,  # OAuth2 uses 'username' field for email
#         password=form_data.password
#     )

#     user = auth_backend.authenticate(db, credentials)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Generate JWT access token
#     access_token = security.create_access_token(data={"sub": user.id})

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#     }

