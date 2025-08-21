# app/routers/patients.py
"""
Patient-related endpoints.

- All routes operate on Patient profile (independent of authentication backend).
- Requires user to be authenticated (JWT/B2C).
- Provides CRUD operations for Patient profile only.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas import schemas
from app.crud import crud
from app.core.dependencies import get_current_user, get_current_patient_or_409
from app.core.database import get_db
from app.models.models import Patient, User

router = APIRouter(prefix="/patients", tags=["Patients"])


# ----------------------------------------
# Create Patient Profile (after signup)
# ----------------------------------------
@router.post("/", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient_profile(
    payload: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a patient profile for the authenticated user.
    - Only allowed if the user does not already have a patient profile.
    - Returns the created Patient profile.
    """
    # Check if profile already exists
    existing = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient profile already exists for this user",
        )

    # Create profile; associate with current user
    patient = crud.create_patient_profile(db, payload, user_id=current_user.id)
    return patient


# ----------------------------------------
# Read Current Patient Profile
# ----------------------------------------
@router.get("/me", response_model=schemas.PatientOut)
def read_current_patient_profile(
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Returns the current user's patient profile.
    - Uses get_current_patient_or_409 dependency to ensure profile exists.
    """
    return patient


# ----------------------------------------
# Update Current Patient Profile
# ----------------------------------------
@router.patch("/me", response_model=schemas.PatientOut)
def update_current_patient_profile(
    payload: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Partially updates the current user's patient profile.
    - Only fields provided in the payload are updated.
    - Password update is ignored here; auth layer handles password changes.
    """
    updated_patient = crud.update_patient(db, patient, payload)
    return updated_patient


# ----------------------------------------
# Delete Current Patient Profile
# ----------------------------------------
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_patient_profile(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Deletes the current user's patient profile.
    - User record remains; only profile is deleted.
    """
    crud.delete_patient(db, patient)
    return None


# ----------------------------------------
# List all patients (optional, admin-only style)
# ----------------------------------------
@router.get("/", response_model=List[schemas.PatientOut])
def list_all_patients(
    db: Session = Depends(get_db),
):
    """
    Returns a list of all patient profiles.
    - Could be restricted to admin users in the future.
    """
    return crud.list_patients(db)
