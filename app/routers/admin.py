# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.schemas import DoctorCreate, DoctorOut, SlotCreate, SlotOut
from app.models.models import Doctor
from app.core.database import get_db
from app.crud import crud_admin  # Use your unified CRUD

router = APIRouter(prefix="/admin", tags=["Admin"])

# -------------------------
# Add Doctor
# -------------------------
@router.post("/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def add_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = crud_admin.create_doctor(db, payload)
    return doctor

# -------------------------
# List Doctors
# -------------------------
@router.get("/doctors", response_model=List[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    doctors = crud_admin.get_all_doctors(db)
    return doctors

# -------------------------
# Add Slot for Doctor
# -------------------------
@router.post("/doctors/{doctor_id}/slots", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
def add_slot(doctor_id: int, payload: SlotCreate, db: Session = Depends(get_db)):
    slot = crud_admin.create_slot(db, payload, doctor_id)
    if not slot:
        raise HTTPException(status_code=400, detail="Slot already exists for this doctor")
    return slot

# -------------------------
# List Slots for a Doctor
# -------------------------
@router.get("/doctors/{doctor_id}/slots", response_model=List[SlotOut])
def list_slots(doctor_id: int, db: Session = Depends(get_db)):
    slots = crud_admin.get_all_slots(db)
    # Filter only slots for the requested doctor
    return [s for s in slots if s.doctor_id == doctor_id]
