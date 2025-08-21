# SQLAlchemy models. Defines Patient and related DB tables. 

# app/models.py
# ----------------
# SQLAlchemy models after Phase 2.
# We introduce a separate User table and link Patient -> User via user_id (1:1).
# IMPORTANT: Do NOT import anything here that triggers application side-effects.

from sqlalchemy import  Column, Integer, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base  # Base comes from database.py

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