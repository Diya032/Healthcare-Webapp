# app/schemas.py
# ---------------------------------------------------------
# Pydantic models for request/response validation.
# We keep "Auth-related" and "Patient-related" schemas
# separate because in production Azure AD B2C will manage
# users & authentication, while Patients remain our
# domain-specific entity stored in our DB.
# ---------------------------------------------------------

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime


# -------------------------
# PATIENT SCHEMAS (Domain)
# -------------------------

class PatientBase(BaseModel):
    """Shared base fields for patient records."""
    name: str
    age: int
    dob: date
    gender: str
    contact_number: str
    email: EmailStr
    address: Optional[str] = None


class PatientCreate(PatientBase):
    """Payload for creating a new patient record (POST /patients).
    Notice: No password field. Auth is managed separately.
    """
    pass


class PatientUpdate(BaseModel):
    """Payload for partial patient updates (PATCH /patients).
    All fields optional so clients can send only what changes.
    """
    name: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class PatientOut(PatientBase):
    """Response model returned to clients after reading patients."""
    id: int
    # Pydantic v2 config: allow ORM → Pydantic conversion
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# AUTH SCHEMAS (Users/JWT)
# -------------------------
# These are temporary while we mock login/signup.
# Later replaced by Azure AD B2C-issued JWTs.
# -------------------------

class UserCreate(BaseModel):
    """Signup payload (used only if we manage auth locally)."""
    email: EmailStr
    password: str  # Will be hashed before storage, don't double hash (mistake)

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    # NOT included password field for security


class LoginSchema(BaseModel):
    """Login payload: exchange email+password for JWT."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT access token returned after login."""
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenData(BaseModel):
    """Payload extracted from JWT (e.g. user_id or email)."""
    email: Optional[str] = None


# -------------------------
# MEDICAL HISTORY SCHEMAS 
# -------------------------

class MedicalHistoryBase(BaseModel):
    """Base fields for medical history records."""
    condition: str
    diagnosis_date: date
    medications: Optional[str] = None
    allergies: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None

class MedicalHistoryCreate(MedicalHistoryBase):
    """Payload for creating a new medical history model"""
    pass 

class MedicalHistoryUpdate(BaseModel):
    condition: Optional[str] = None
    diagnosis_date: Optional[date] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None

class MedicalHistoryOut(MedicalHistoryBase):
    """Response model for medical history records."""
    id: int
    # patient_id: int # Link to the patient records BUT we don't expose this to the patient
    # Pydantic v2 config: allow ORM -> Pydantic conversion
    model_config = ConfigDict(from_attributes= True)

# -------------------------


# -------------------------
# SLOT SCHEMAS
# -------------------------
class SlotOut(BaseModel):
    id: int
    doctor_id: int
    datetime: datetime
    is_booked: bool   # cast Integer (0/1) -> bool in response

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# APPOINTMENT SCHEMAS
# -------------------------
class AppointmentBase(BaseModel):
    patient_name: str
    patient_email: EmailStr


class AppointmentCreate(AppointmentBase):
    slot_id: int


class AppointmentOut(AppointmentBase):
    id: int
    slot_id: int
    slot: SlotOut
    booked_at: datetime

    model_config = ConfigDict(from_attributes=True)
