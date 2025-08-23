from typing import List
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from datetime import datetime, timedelta, timezone
from app.models.models import Doctor, Slot
from fastapi import HTTPException

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

def get_all_doctors(db: Session):
    """
    Returns a list of all doctors in the database.
    """
    return db.query(models.Doctor).order_by(models.Doctor.name).all()

# Update doctor
def update_doctor(db: Session, doctor_id: int, name: str = None, specialty: str = None):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if name:
        doctor.name = name
    if specialty:
        doctor.specialty = specialty
    db.commit()
    db.refresh(doctor)
    return doctor

# Delete doctor and all related slots
def delete_doctor(db: Session, doctor_id: int):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return True



# -----------------------------
# Helper
# -----------------------------
def round_to_interval(dt: datetime, interval_minutes: int) -> datetime:
    """Round datetime down to nearest interval (e.g., 30 mins)."""
    discard = timedelta(
        minutes=dt.minute % interval_minutes,
        seconds=dt.second,
        microseconds=dt.microsecond
    )
    return dt - discard

# -----------------------------
# Slots CRUD
# -----------------------------

def create_slot(db: Session, payload: schemas.SlotCreate, doctor_id: int) -> dict:
    """
    Create a single slot for a doctor.
    - Only future slots allowed.
    - Existing slots are skipped to prevent redundancy.
    Returns a dictionary ready for SlotOut schema.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    aligned_time = round_to_interval(payload.datetime, 30)
    now = datetime.now(timezone.utc)

    if aligned_time < now:
        raise HTTPException(status_code=400, detail="Cannot create a slot in the past")

    # Skip if slot already exists
    existing = db.query(Slot).filter(
        Slot.doctor_id == doctor_id,
        Slot.datetime == aligned_time
    ).first()
    if existing:
        return {
            "id": existing.id,
            "doctor_id": existing.doctor_id,
            "datetime": existing.datetime,
            "is_booked": existing.is_booked,
            "doctor_name": doctor.name,
            "specialty": doctor.specialty
        }

    # Create new slot
    slot = Slot(
        doctor_id=doctor_id,
        datetime=aligned_time,
        is_booked=0
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)

    return {
        "id": slot.id,
        "doctor_id": slot.doctor_id,
        "datetime": slot.datetime,
        "is_booked": slot.is_booked,
        "doctor_name": doctor.name,
        "specialty": doctor.specialty
    }


def create_bulk_slots(db: Session, payload: schemas.BulkSlotCreate) -> List[dict]:
    """
    Create multiple slots for a doctor in a given date and time interval.
    - Only future slots are created.
    - Existing slots are skipped to prevent redundancy.
    Returns a list of dicts ready for SlotOut schema.
    """
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    slots_out = []
    now = datetime.now(timezone.utc)
    current_time = datetime.combine(payload.date, payload.start_time)
    end_time = datetime.combine(payload.date, payload.end_time)

    new_slots = []
    while current_time < end_time:
        aligned_time = round_to_interval(current_time, payload.interval_minutes)

        # Skip past times
        if aligned_time < now:
            current_time += timedelta(minutes=payload.interval_minutes)
            continue

        # Skip if slot already exists
        existing = db.query(Slot).filter(
            Slot.doctor_id == payload.doctor_id,
            Slot.datetime == aligned_time
        ).first()
        if not existing:
            slot = Slot(
                doctor_id=payload.doctor_id,
                datetime=aligned_time,
                is_booked=0
            )
            db.add(slot)
            new_slots.append(slot)

        current_time += timedelta(minutes=payload.interval_minutes)

    # Commit all new slots at once
    db.commit()

    for slot in new_slots:
        db.refresh(slot)
        slots_out.append({
            "id": slot.id,
            "doctor_id": slot.doctor_id,
            "datetime": slot.datetime,
            "is_booked": slot.is_booked,
            "doctor_name": doctor.name,
            "specialty": doctor.specialty
        })

    return slots_out


def get_all_slots(db: Session, only_future: bool = True) -> List[dict]:
    """
    Retrieve all slots with doctor info.
    If only_future=True, returns only slots with datetime >= now.
    """
    query = db.query(Slot).join(Doctor)
    if only_future:
        query = query.filter(Slot.datetime >= datetime.utcnow())

    db_slots = query.order_by(Slot.datetime).all()

    slots_out = []
    for s in db_slots:
        slots_out.append({
            "id": s.id,
            "doctor_id": s.doctor_id,
            "datetime": s.datetime,
            "is_booked": s.is_booked,
            "doctor_name": s.doctor.name,
            "specialty": s.doctor.specialty
        })
    return slots_out

# Update a slot (datetime or availability)
def update_slot(db: Session, slot_id: int, new_datetime: datetime = None, is_booked: int = None):
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if new_datetime:
        slot.datetime = new_datetime
    if is_booked is not None:
        slot.is_booked = is_booked
    
    db.commit()
    db.refresh(slot)
    return {
        "id": slot.id,
        "doctor_id": slot.doctor_id,
        "datetime": slot.datetime,
        "is_booked": slot.is_booked,
        "doctor_name": slot.doctor.name,
        "specialty": slot.doctor.specialty
    }

# Delete a slot
def delete_slot(db: Session, slot_id: int):
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    db.delete(slot)
    db.commit()
    return True


def delete_future_slots_for_doctor(db: Session, doctor_id: int, days: int):
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)

    slots = db.query(Slot).filter(
        Slot.doctor_id == doctor_id,
        Slot.datetime >= now,
        Slot.datetime <= end_date
    ).all()

    for s in slots:
        db.delete(s)
    db.commit()
    return len(slots)  # number of deleted slots





