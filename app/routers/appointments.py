# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.models.models import Patient, Appointment, Slot
from app.schemas.schemas import SlotOut, AppointmentCreate, AppointmentOut, PatientAppointments
from app.core.dependencies import get_current_patient_or_409
from app.core.database import get_db
from app.crud import crud_appointment as crud

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# -------------------------------
# View available slots
# -------------------------------
@router.get("/slots", response_model=List[SlotOut])
def list_available_slots(
    specialty: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")

    slots = crud.get_available_slots(db, specialty=specialty, date=date)
    return [
        SlotOut(
            id=s.id,
            doctor_id=s.doctor_id,
            datetime=s.datetime,
            is_booked=s.is_booked,
            doctor_name=s.doctor.name,
            specialty=s.doctor.specialty
        )
        for s in slots
    ]


# -------------------------------
# Book an appointment
# -------------------------------
@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    try:
        appointment = crud.create_appointment(
            db=db,
            patient_id=patient.id,
            slot_id=payload.slot_id,
            reason=getattr(payload, "reason", None)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return AppointmentOut(
        id=appointment.id,
        patient_name=patient.name,
        patient_email=patient.email,
        reason=getattr(appointment, "reason", None),
        slot=SlotOut(
            id=appointment.slot.id,
            doctor_id=appointment.slot.doctor_id,
            datetime=appointment.slot.datetime,
            is_booked=appointment.slot.is_booked,
            doctor_name=appointment.slot.doctor.name,
            specialty=appointment.slot.doctor.specialty
        ),
        booked_at=appointment.booked_at
    )


# -------------------------------
# View current patient's appointments (upcoming & past)
# -------------------------------
@router.get("/me", response_model=PatientAppointments)
@router.get("/me", response_model=PatientAppointments)
def get_my_appointments(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient_or_409)
):
    upcoming = crud.get_patient_appointments(db, patient.id, only_future=True)
    past = crud.get_patient_appointments(db, patient.id, only_future=False)

    def to_out(a):
        return AppointmentOut(
            id=a.id,
            patient_name=patient.name,
            patient_email=patient.email,
            reason=getattr(a, "reason", None),
            slot=SlotOut(
                id=a.slot.id,
                doctor_id=a.slot.doctor_id,
                datetime=a.slot.datetime,
                is_booked=a.slot.is_booked,
                doctor_name=a.slot.doctor.name,
                specialty=a.slot.doctor.specialty
            ),
            booked_at=a.booked_at
        )

    return PatientAppointments(
        upcoming=[to_out(a) for a in upcoming],
        past=[to_out(a) for a in past]
    )



# -------------------------------
# Cancel an appointment
# -------------------------------
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this appointment")

    crud.cancel_appointment(db, appointment_id)
    return None
