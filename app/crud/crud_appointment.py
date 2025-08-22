# app/crud/crud_appointments.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

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
    query = db.query(models.Slot).join(models.Doctor)
    if specialty:
        query = query.filter(models.Doctor.specialty == specialty)
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        query = query.filter(models.Slot.datetime >= start_date,
                             models.Slot.datetime < end_date)
    slots = query.filter(models.Slot.is_booked == 0).order_by(models.Slot.datetime).all()

    cleaned_slots = []
    seen_times = set()
    for s in slots:
        if (s.doctor_id, s.datetime) not in seen_times:
            seen_times.add((s.doctor_id, s.datetime))
            cleaned_slots.append(s)
    return cleaned_slots

def get_slot_by_id(db: Session, slot_id: int):
    return db.query(models.Slot).filter(models.Slot.id == slot_id).first()

def create_slot(db: Session, slot: schemas.SlotCreate):
    aligned_time = round_to_interval(slot.datetime, 30)
    existing = db.query(models.Slot).filter(
        models.Slot.doctor_id == slot.doctor_id,
        models.Slot.datetime == aligned_time
    ).first()
    if existing:
        return None
    db_slot = models.Slot(
        doctor_id=slot.doctor_id,
        datetime=aligned_time,
        is_booked=0
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def create_bulk_slots(db: Session, bulk_data: schemas.BulkSlotCreate):
    slots = []
    start_dt = datetime.combine(bulk_data.date, bulk_data.start_time)
    end_dt = datetime.combine(bulk_data.date, bulk_data.end_time)
    start_dt = round_to_interval(start_dt, bulk_data.interval_minutes)

    while start_dt < end_dt:
        existing = db.query(models.Slot).filter(
            models.Slot.doctor_id == bulk_data.doctor_id,
            models.Slot.datetime == start_dt
        ).first()
        if not existing:
            slot = models.Slot(
                doctor_id=bulk_data.doctor_id,
                datetime=start_dt,
                is_booked=0
            )
            db.add(slot)
            slots.append(slot)
        start_dt += timedelta(minutes=bulk_data.interval_minutes)

    db.commit()
    for s in slots:
        db.refresh(s)
    return slots

# -----------------------------
# Doctor CRUD
# -----------------------------

def update_doctor(db: Session, doctor_id: int, name: str = None, specialty: str = None):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        return None
    if name:
        doctor.name = name
    if specialty:
        doctor.specialty = specialty
    db.commit()
    db.refresh(doctor)
    return doctor

def delete_doctor(db: Session, doctor_id: int):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        return None
    db.delete(doctor)
    db.commit()
    return True

# -----------------------------
# Appointment CRUD
# -----------------------------

def create_appointment(db: Session, patient_id: int, slot_id: int, reason: str = None):
    """Book an appointment, mark slot booked"""
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        raise ValueError("Slot does not exist")
    if slot.is_booked:
        raise ValueError("Slot is already booked")

    appointment = models.Appointment(
        patient_id=patient_id,
        slot_id=slot_id,
        booked_at=datetime.utcnow()
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

def get_patient_appointments(db: Session, patient_id: int):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

def cancel_appointment(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None
    if appointment.slot:
        appointment.slot.is_booked = 0
    db.delete(appointment)
    db.commit()
    return appointment
