from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def create_medical_history(db: Session, payload: schemas.MedicalHistoryCreate, patient_id: int) -> models.MedicalHistory:
    """
    Creates a new medical history recordfro patient."""
    db_medical_history = models.MedicalHistory(
        patient_id=patient_id,
        condition=payload.condition,
        diagnosis_date=payload.diagnosis_date,
        medications=payload.medications,
        allergies=payload.allergies,
        treatment=payload.treatment,
        notes=payload.notes
    )

    db.add(db_medical_history)
    db.commit()
    db.refresh(db_medical_history)
    return db_medical_history


# ----------------------------
# READ (GET BY ID)
# ----------------------------
def get_medical_history(db: Session, history_id: int) -> models.MedicalHistory | None:
    """
    Fetch a single medical history record by its ID.
    """
    return db.query(models.MedicalHistory).filter(
        models.MedicalHistory.id == history_id
    ).first()


# ----------------------------
# READ (GET ALL BY PATIENT)
# ----------------------------
def get_medical_histories_by_patient(db: Session, patient_id: int) -> list[models.MedicalHistory]:
    """
    Fetch all medical history records for a specific patient.
    """
    return db.query(models.MedicalHistory).filter(
        models.MedicalHistory.patient_id == patient_id
    ).all()


# ----------------------------
# UPDATE
# ----------------------------
def update_medical_history(
    db: Session,
    payload: models.MedicalHistory,
    updates: schemas.MedicalHistoryUpdate,
) -> models.MedicalHistory:
    """
    Update an existing medical history record.
    """
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(payload, field):
            setattr(payload, field, value)

    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# ----------------------------
# DELETE
# ----------------------------
def delete_medical_history(db: Session, history_id: int) -> bool:
    """
    Delete a medical history record by ID.
    Returns True if deleted, False if not found.
    """
    db_medical_history = db.query(models.MedicalHistory).filter(
        models.MedicalHistory.id == history_id
    ).first()

    if not db_medical_history:
        return False

    db.delete(db_medical_history)
    db.commit()
    return True