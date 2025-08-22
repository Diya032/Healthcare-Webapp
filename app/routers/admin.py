# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.schemas.schemas import DoctorCreate, DoctorOut, SlotCreate, SlotOut, BulkSlotCreate
from app.models.models import Doctor
from app.core.database import get_db
from app.crud import crud_admin  # your unified CRUD

router = APIRouter(prefix="/admin", tags=["Admin"])


# -------------------------
# Add Doctor
# -------------------------
@router.post("/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def add_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    return crud_admin.create_doctor(db, payload)


# -------------------------
# List Doctors
# -------------------------
@router.get("/doctors", response_model=List[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    return crud_admin.get_all_doctors(db)


# -------------------------
# Add Single Slot
# -------------------------
@router.post("/doctors/{doctor_id}/slots", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
def add_slot(doctor_id: int, payload: SlotCreate, db: Session = Depends(get_db)):
    slot = crud_admin.create_slot(db, payload, doctor_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot already exists or is in the past"
        )
    return slot


# -------------------------
# Add Bulk Slots
# -------------------------
@router.post("/doctors/{doctor_id}/slots/bulk", response_model=List[SlotOut], status_code=status.HTTP_201_CREATED)
def add_bulk_slots(doctor_id: int, payload: BulkSlotCreate, db: Session = Depends(get_db)):
    """
    Create multiple slots for a doctor in a given date and time range.
    - Skips past times
    - Skips duplicate slots
    - Returns all created slots with doctor info
    """
    created_slots = crud_admin.create_bulk_slots(db, payload)
    if not created_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No new slots were created (all slots may already exist or are in the past)"
        )
    return created_slots


# -------------------------
# List Slots for a Doctor
# -------------------------
@router.get("/doctors/{doctor_id}/slots", response_model=List[SlotOut])
def list_slots(doctor_id: int, db: Session = Depends(get_db), only_future: bool = True):
    """
    List all slots for a doctor.
    Use `only_future=False` to include past slots.
    """
    all_slots = crud_admin.get_all_slots(db, only_future=only_future)
    return [s for s in all_slots if s["doctor_id"] == doctor_id]


# -------------------------
# List Past and Future Slots Separately
# -------------------------
@router.get("/doctors/{doctor_id}/slots/separated", response_model=dict)
def list_slots_separated(doctor_id: int, db: Session = Depends(get_db)):
    """
    Returns:
    {
        "future": [...SlotOut...],
        "past": [...SlotOut...]
    }
    """
    all_slots = crud_admin.get_all_slots(db, only_future=False)
    future_slots = []
    past_slots = []
    now = datetime.now(timezone.utc)
    for s in all_slots:
        if s["doctor_id"] != doctor_id:
            continue
        if s["datetime"] >= now:
            future_slots.append(s)
        else:
            past_slots.append(s)
    return {"future": future_slots, "past": past_slots}
