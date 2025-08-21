from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas import schemas
from app.models.models import Patient, Appointment
from app.crud import crud_appointment
from app.core.dependencies import get_current_patient_or_409
from app.core.database import get_db

router = APIRouter(prefix="/appointments", tags=["Appointments"])


# ----------------------------------------
# Book a new appointment
# ----------------------------------------
@router.post("/", response_model=schemas.AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Book an appointment for the current patient.
    - Slot must exist and be available.
    - Returns the booked appointment details.
    """
    try:
        appointment = crud_appointment.create_appointment(
            db=db,
            patient_id=patient.id,
            slot_id=payload.slot_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return appointment


# ----------------------------------------
# List all appointments for current patient
# ----------------------------------------
@router.get("/", response_model=List[schemas.AppointmentOut])
def list_patient_appointments(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Returns all appointments booked by the current patient.
    """
    return crud_appointment.get_patient_appointments(db, patient_id=patient.id)


# ----------------------------------------
# Cancel an appointment
# ----------------------------------------
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409),
):
    """
    Cancels an appointment.
    - Only the owner patient can cancel.
    - Frees the slot automatically.
    """
    appointment = crud_appointment.get_appointment(db, appointment_id)
    if not appointment or appointment.patient_id != patient.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    crud_appointment.cancel_appointment(db, appointment_id)
    return None
