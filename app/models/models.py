# SQLAlchemy models. Defines Patient and related DB tables. 

# app/models.py
# ----------------
# SQLAlchemy models after Phase 2.
# We introduce a separate User table and link Patient -> User via user_id (1:1).
# IMPORTANT: Do NOT import anything here that triggers application side-effects.

from sqlalchemy import  Column, Integer, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, func, Enum, Text, BigInteger, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base  # Base comes from database.py
from datetime import datetime
import enum

class User(Base):
    """
    Authentication/identity table.
    Only credentials & account status live here (NO patient profile info).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)  # single source of truth for email
    hashed_password = Column(String(255), nullable=False)                  # keep existing hashes as-is
    is_active = Column(Boolean, nullable=False, server_default="1")   # simple active flag
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Reverse one-to-one (optional); set uselist=False on Patient side if you want strict 1:1
    patient = relationship("Patient", back_populates="user", uselist=False)


class Patient(Base):
    """
    Domain profile table (no credentials).
    Links to User via user_id (1:1 relationship).
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    # NEW in Phase 2:
    user_id = Column(Integer, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False, unique=True, index=True)

    # --- Domain profile fields (keep what you already had; sample below) ---
    name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String(255), nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String(255), nullable = True, )
    address = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient", cascade="all, delete")

    # Optional: Appointments (1:N relationship)
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    # Optional: Medical Documents (1:N relationship)
    medical_documents = relationship("MedicalDocument", back_populates="patient", cascade="all, delete-orphan")


class MedicalHistory(Base):
    """
    Optional: Separate table for patient medical history.
    Links to Patient via patient_id (many-to-one).
    """
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    condition = Column(String(255), nullable=False)
    diagnosis_date = Column(Date, nullable=True)
    medications = Column(String(255), nullable=True)
    allergies = Column(String(255), nullable= True)
    treatment = Column(String(255), nullable= True)
    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="medical_history")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)

    # one-to-many with slots
    slots = relationship("Slot", back_populates="doctor", cascade="all, delete-orphan")


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    is_booked = Column(Integer, default=0)  # 0 = available, 1 = booked


    # backref to doctor
    doctor = relationship("Doctor", back_populates="slots")

    # one-to-one with appointment
    appointment = relationship("Appointment", back_populates="slot", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("doctor_id", "datetime", name="unique_doctor_slot"),)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Link to Patient (many appointments per patient)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Link to Slot (1:1: one slot = one appointment max)
    slot_id = Column(Integer, ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    reason = Column(Text, nullable=True)  # New field for reason of visit
    booked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    slot = relationship("Slot", back_populates="appointment")







#----------------------------
# blob-storage-di
#----------------------------

class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    file_name = Column(String(255), nullable=False)        # original filename
    blob_key = Column(String(500), nullable=True)         # "patient_id/document_id/filename.pdf"
    content_type = Column(String(100), nullable=True)
    # file_size = Column(BigInteger, nullable=True)

    upload_status = Column(String(50), nullable=False, server_default="pending")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="medical_documents")
    document_intelligence = relationship("DocumentIntelligence", back_populates="medical_document", uselist=False, cascade="all, delete-orphan")


class DocumentIntelligence(Base):
    __tablename__ = "document_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer,
        ForeignKey("medical_documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One-to-one mapping: one DI result per document
        index=True
    )

    status = Column(String(50), nullable=False, server_default="processing")  # "processing", "completed", "failed"
    raw_result = Column(JSON, nullable=True)       # full DI JSON output
    # summary_text = Column(Text, nullable=True)     # optional flattened summary for quick frontend display
    # confidence_score = Column(Float, nullable=True)  # optional: aggregate confidence if needed

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship back to MedicalDocument
    medical_document = relationship("MedicalDocument", back_populates="document_intelligence")
