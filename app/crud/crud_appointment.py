from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from app.models import models
from app.schemas import schemas

# -----------------------------
# Slot Helpers
# -----------------------------
def round_to_interval(dt: datetime, interval_minutes: int):
    """Round datetime down to nearest interval (e.g., 30 mins)"""
    discard = timedelta(
        minutes=dt.minute % interval_minutes,
        seconds=dt.second,
        microseconds=dt.microsecond
    )
    return dt - discard

# -----------------------------
# Slots CRUD
# -----------------------------
def get_available_slots(db: Session, specialty: str = None, date: str = None):
    now = datetime.now(timezone.utc)
    query = db.query(models.Slot).join(models.Doctor)

    if specialty:
        query = query.filter(models.Doctor.specialty == specialty)
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = start_date + timedelta(days=1)
        query = query.filter(models.Slot.datetime >= start_date,
                             models.Slot.datetime < end_date)

    # Only future slots
    query = query.filter(models.Slot.is_booked == 0, models.Slot.datetime >= now)
    slots = query.order_by(models.Slot.datetime).all()

    # Deduplicate
    cleaned_slots = []
    seen_times = set()
    for s in slots:
        if (s.doctor_id, s.datetime) not in seen_times:
            seen_times.add((s.doctor_id, s.datetime))
            cleaned_slots.append(s)
    return cleaned_slots

def get_slot_by_id(db: Session, slot_id: int):
    return db.query(models.Slot).filter(models.Slot.id == slot_id).first()



# -----------------------------
# Appointment CRUD
# -----------------------------
def create_appointment(db: Session, patient_id: int, slot_id: int):
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        raise ValueError("Slot does not exist")
    if slot.is_booked:
        raise ValueError("Slot is already booked")

    # Prevent same patient from booking another slot at the same datetime
    conflict = db.query(models.Appointment).join(models.Slot).filter(
        models.Appointment.patient_id == patient_id,
        models.Slot.datetime == slot.datetime
    ).first()

    if conflict:
        raise ValueError("You already have an appointment at this time")

    appointment = models.Appointment(
        patient_id=patient_id,
        slot_id=slot_id,
        booked_at=datetime.now(timezone.utc),
        # reason=reason
    )
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

def get_patient_appointments(db: Session, patient_id: int, only_future: bool = True):
    query = db.query(models.Appointment).join(models.Slot).filter(
        models.Appointment.patient_id == patient_id
    )

    now = datetime.now(timezone.utc)
    if only_future:
        query = query.filter(models.Slot.datetime >= now)
    else:
        query = query.filter(models.Slot.datetime < now)

    return query.order_by(models.Slot.datetime).all()


def cancel_appointment(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None
    if appointment.slot:
        appointment.slot.is_booked = 0
    db.delete(appointment)
    db.commit()
    return appointment
