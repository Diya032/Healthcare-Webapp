from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import crud_document_intelligence as crud
from app.crud import crud_medical_documents
from app.schemas import schemas_blob_di as schemas
from app.core.database import get_db
from app.core.dependencies import get_current_patient_or_409
from app.core.config import settings
from app.models.models import Patient

from app.blob_di.Prepare_JSON import prepare_overlay_json
from app.blob_di.blob_sas import generate_sas_url_for_di

router = APIRouter(prefix="/docu_intelligence", tags=["Document Intelligence"])

# -----------------------------
# Create doc intelligence record
# -----------------------------
# @router.post("/", response_model=schemas.DocumentIntelligenceOut)
# def create_docu_intelligence(
#     record: schemas.DocumentIntelligenceCreate,
#     current_patient: Patient = Depends(get_current_patient_or_409),
#     db: Session = Depends(get_db)
# ):
#     # Ensure document belongs to current patient
#     doc = crud_medical_documents.get_medical_document(db, record.document_id)
#     if not doc or doc.patient_id != current_patient.id:
#         raise HTTPException(status_code=404, detail="Document not found for this patient")

#     return crud.create_document_intelligence(db, record)


# -----------------------------
# Read doc intelligence by document_id
# -----------------------------
@router.get("/{document_id}", response_model=schemas.DocumentIntelligenceOut)
def get_docu_intelligence(
    document_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient_or_409)
):
    # 1️⃣ Fetch the document and ensure ownership
    db_doc = crud_medical_documents.get_medical_document(db, document_id)
    if not db_doc or db_doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2️⃣ Fetch DI record
    di_record = crud.get_document_intelligence(db, document_id)
    if not di_record:
        # Analysis may still be processing
        return {
            "document_id": document_id,
            "status": "processing",
            "raw_result": None,
            # "summary_text": None,
            # "confidence_score": None,
            "created_at": None,
            "updated_at": None
        }

    # 3️⃣ Return completed DI result
    return di_record


# -----------------------------
# Delete doc intelligence record
# -----------------------------
@router.delete("/{document_id}", status_code=204)
def delete_docu_intelligence(
    document_id: int,
    current_patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    doc = crud_medical_documents.get_medical_document(db, document_id)
    if not doc or doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found for this patient")

    success = crud.delete_document_intelligence(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return None



@router.get("/{document_id}")
def get_docu_intelligence_overlay(
    document_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient_or_409)
):
    doc = crud_medical_documents.get_medical_document(db, document_id)
    if not doc or doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found")

    di_record = crud.get_document_intelligence(db, document_id)
    print(type(di_record.raw_result))
    
    blob_url = generate_sas_url_for_di(
        container_name="medical-documents",
        blob_name=doc.blob_key,
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        account_key=settings.AZURE_STORAGE_KEY
    )

    raw_result = di_record.raw_result if di_record else None
    if isinstance(raw_result, str):
        import json
        raw_result = json.loads(raw_result)

    return prepare_overlay_json(
        document_id=document_id,
        raw_result=raw_result,
        file_sas_url=blob_url
    )
