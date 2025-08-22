from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from datetime import datetime, timedelta
from app.models.models import Slot

def create_doctor(db: Session, payload: schemas.DoctorCreate) -> models.Doctor:
    """
    Create a new doctor in the system.
    """
    doctor = models.Doctor(
        name=payload.name,
        specialty=payload.specialty
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

def get_doctor_by_id(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def list_doctors(db: Session):
    return db.query(models.Doctor).all()

def get_all_doctors(db: Session):
    """
    Returns a list of all doctors in the database.
    """
    return db.query(models.Doctor).order_by(models.Doctor.name).all()


def round_to_interval(dt: datetime, interval_minutes: int):
    """Round datetime down to nearest interval."""
    discard = timedelta(
        minutes=dt.minute % interval_minutes,
        seconds=dt.second,
        microseconds=dt.microsecond
    )
    return dt - discard

def create_slot(db: Session, payload: schemas.SlotCreate, doctor_id: int) -> models.Slot:
    """
    Create a slot for a given doctor.
    """
    aligned_time = round_to_interval(payload.datetime, 30)

    # Check if slot already exists
    existing = db.query(models.Slot).filter(
        models.Slot.doctor_id == doctor_id,
        models.Slot.datetime == aligned_time
    ).first()
    if existing:
        return existing  # or raise an error if you want uniqueness

    slot = models.Slot(
        doctor_id=doctor_id,
        datetime=aligned_time,
        is_booked=0
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def get_all_slots(db: Session):
    """Return all slots in the database"""
    return db.query(Slot).all()