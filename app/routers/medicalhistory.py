from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import models
from app.crud import crud_medicals
from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/medical-history", tags=["Medical History"])


# ----------------------------
# CREATE
# ----------------------------
@router.post("/", response_model=schemas.MedicalHistoryOut)
def create_medical_history(
    payload: schemas.MedicalHistoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # patient_id comes from logged-in user, not request body
    patient = current_user.patient
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an associated patient profile."
        )

    return crud_medicals.create_medical_history(
        db=db,
        patient_id=patient.id,
        payload=payload
    )


# ----------------------------
# READ (all for current patient)
# ----------------------------
@router.get("/", response_model=list[schemas.MedicalHistoryOut])
def get_my_medical_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = current_user.patient
    return crud_medicals.get_medical_histories_by_patient(
        db=db,
        patient_id=patient.id
    )


# ----------------------------
# UPDATE (only own record)
# ----------------------------
@router.put("/{history_id}", response_model=schemas.MedicalHistoryOut)
def update_medical_history(
    history_id: int,
    payload: schemas.MedicalHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = current_user.patient
    db_mh = crud_medicals.get_medical_history(db, history_id)

    if not db_mh or db_mh.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Medical history not found.")

    return crud_medicals.update_medical_history(
        db=db,
        payload=db_mh,
        updates=payload
    )


# ----------------------------
# DELETE (only own record)
# ----------------------------
@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = current_user.patient
    db_mh = crud_medicals.get_medical_history(db, history_id)

    if not db_mh or db_mh.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Medical history not found.")

    crud_medicals.delete_medical_history(db, history_id)
    return None
