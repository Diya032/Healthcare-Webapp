from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models import models
from app.schemas import schemas

# -----------------------------
# Appointment CRUD
# -----------------------------

def create_appointment(
    db: Session,
    patient_id: int,
    slot_id: int,
    reason: str = None
) -> models.Appointment:
    """
    Book an appointment for a patient with a given slot.
    Ensures one appointment per slot (unique constraint on slot_id).
    """

    # Check if slot exists and is available
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id).first()
    if not slot:
        raise ValueError("Slot does not exist")
    if slot.is_booked:
        raise ValueError("Slot is already booked")

    # Create appointment
    appointment = models.Appointment(
        patient_id=patient_id,
        slot_id=slot_id,
        booked_at=datetime.utcnow()
    )

    # Mark slot as booked
    slot.is_booked = 1

    try:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
    except IntegrityError:
        db.rollback()
        raise ValueError("Slot already has an appointment")

    return appointment


def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def get_patient_appointments(db: Session, patient_id: int):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()


def cancel_appointment(db: Session, appointment_id: int):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        return None

    # Unbook the slot
    if appointment.slot:
        appointment.slot.is_booked = 0

    db.delete(appointment)
    db.commit()
    return appointment
