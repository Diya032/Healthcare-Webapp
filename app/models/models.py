# SQLAlchemy models. Defines Patient and related DB tables. 

# app/models.py
# ----------------
# SQLAlchemy models after Phase 2.
# We introduce a separate User table and link Patient -> User via user_id (1:1).
# IMPORTANT: Do NOT import anything here that triggers application side-effects.

from sqlalchemy import  Column, Integer, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, func, Enum, Text
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
    email = Column(String, nullable=False, unique=True, index=True)  # single source of truth for email
    hashed_password = Column(String, nullable=False)                  # keep existing hashes as-is
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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True, index=True)

    # --- Domain profile fields (keep what you already had; sample below) ---
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable = True, )
    address = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient", cascade="all, delete")

    # Optional: Appointments (1:N relationship)
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class MedicalHistory(Base):
    """
    Optional: Separate table for patient medical history.
    Links to Patient via patient_id (many-to-one).
    """
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    condition = Column(String, nullable=False)
    diagnosis_date = Column(Date, nullable=True)
    medications = Column(String, nullable=True)
    allergies = Column(String, nullable= True)
    treatment = Column(String, nullable= True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="medical_history")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)

    # ✅ one-to-many with slots
    slots = relationship("Slot", back_populates="doctor", cascade="all, delete-orphan")


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    is_booked = Column(Integer, default=0)  # 0 = available, 1 = booked


    # ✅ backref to doctor
    doctor = relationship("Doctor", back_populates="slots")

    # ✅ one-to-one with appointment
    appointment = relationship("Appointment", back_populates="slot", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("doctor_id", "datetime", name="unique_doctor_slot"),)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Link to Patient (many appointments per patient)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Link to Slot (1:1: one slot = one appointment max)
    slot_id = Column(Integer, ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    booked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    slot = relationship("Slot", back_populates="appointment")


