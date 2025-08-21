# CRUD operations. Contains database logic for Patients. 

# app/crud.py
# ------------------------------------------------------
# CRUD functions that talk to the DB via SQLAlchemy.
# Keep these pure — no FastAPI/HTTP concerns here.
# ------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import models
from app.schemas import schemas
# from app.core.security import hash_password

# ---- Read helpers ----

def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def get_patient_by_contact(db: Session, contact_number: str) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.contact_number == contact_number).first()

def list_patients(db: Session, skip: int = 0, limit: int = 100) -> list[models.Patient]:
    return db.query(models.Patient).offset(skip).limit(limit).all()

# ---- Create ----

# ---- Create Patient Profile ---- (later azure adb2c version)
def create_patient_profile(db: Session, payload: schemas.PatientCreate, user_id: int) -> models.Patient:
    """
    Creates a Patient profile associated with a User (user_id).
    Used in /patients POST when profile is separate from auth.

    Args:
        db: SQLAlchemy session
        payload: PatientCreate Pydantic model (no password)
        user_id: ID of the owning user

    Returns:
        Newly created Patient instance
    """
    patient = models.Patient(
        name=payload.name,
        age=payload.age,
        dob= payload.dob,
        gender=payload.gender,
        contact_number=payload.contact_number,
        email=payload.email,
        address=payload.address,
        user_id=user_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ---- Update (partial) ----

def update_patient(db: Session, patient: models.Patient, payload: schemas.PatientUpdate) -> models.Patient:
    """
    Partially updates a patient. If password present, re-hash it.
    Only changes fields that are provided.
    """
    # Update simple fields if provided
    for field in ["name", "age", "gender", "contact_number", "email", "address", "dob"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(patient, field, value)

    # Handle password update if provided (Due to user and patient separation, will not be used here but in crud_user.py)
    # if payload.password:
    #     patient.password_hash = hash_password(payload.password)

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

# ---- Delete ----

def delete_patient(db: Session, patient: models.Patient) -> None:
    db.delete(patient)
    db.commit()

# ---- Auth ---- (DONE BY authenticate_backend in app/core/ now)

# def authenticate(db: Session, email: str, password: str) -> models.Patient | None:
#     """
#     Returns the patient if credentials are valid, else None.
#     """
#     patient = get_patient_by_email(db, email)
#     if not patient:
#         return None
#     if not verify_password(password, patient.password_hash):
#         return None
#     return patient

# ---- Uniqueness guard (use in router before writes) ----

def email_or_contact_exists(db: Session, email: str, contact_number: str, exclude_id: int | None = None) -> bool:
    """
    True if another patient already has the same email or contact.
    exclude_id: ignore this patient (useful for updates).
    """
    q = db.query(models.Patient).filter(
        or_(models.Patient.email == email, models.Patient.contact_number == contact_number)
    )
    if exclude_id is not None:
        q = q.filter(models.Patient.id != exclude_id)
    return db.query(q.exists()).scalar()


# ------------------------------------------------------
# Additional helper functions to support auth & dependencies. USED IN dependecies.py
# ------------------------------------------------------

# # ----------------------------
# # User lookup by ID (IS IN CRUD_USER.py)
# # ----------------------------
# def get_user_by_id(db: Session, user_id: int) -> models.User | None:
#     """
#     Retrieve a User object by its primary key (id).
#     Used in get_current_user dependency.
    
#     Args:
#         db: SQLAlchemy session
#         user_id: primary key of the User

#     Returns:
#         User instance if found, else None
#     """
#     return db.query(models.User).filter(models.User.id == user_id).first()


# ----------------------------
# Patient lookup by user_id
# ----------------------------
def get_patient_by_user_id(db: Session, user_id: int) -> models.Patient | None:
    """
    Retrieve a Patient object associated with a given User.
    Used in get_current_patient_or_409 dependency.

    Args:
        db: SQLAlchemy session
        user_id: ID of the user whose patient profile is requested

    Returns:
        Patient instance if exists, else None
    """
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()