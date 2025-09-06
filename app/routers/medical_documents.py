
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime, timezone

from app.crud import crud_medical_documents
from app.schemas import schemas_blob_di as schemas
from app.core.database import get_db
from app.core import database
from app.core.config import settings
from app.core.dependencies import get_current_patient_or_409
from app.models.models import DocumentIntelligence, Patient

from app.blob_di.blob_sas import generate_sas_url, generate_sas_url_for_di
from app.blob_di.blob_di_client import analyze_document  # Our DI SDK wrapper in blob_di_client.py

router = APIRouter(prefix="/medical_documents", tags=["Medical Documents"])


# -----------------------------
# Request SAS upload (RETURN SAS URL TO FRONTEND FOR DIRECT UPLOAD)
# -----------------------------
@router.post("/request-upload", response_model=schemas.MedicalDocumentUploadResponse)
def request_upload(
    document: schemas.MedicalDocumentUploadIn,
    current_patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    # Build internal schema with patient_id injected
    doc_create = schemas.MedicalDocumentCreate(
        **document.model_dump(),
        patient_id=current_patient.id
    )


    # 1. Create DB record
    db_doc = crud_medical_documents.create_medical_document(db, doc_create)

    # 2. Generate blob_key
    db_doc.blob_key = f"{current_patient.id}/{db_doc.id}/{document.file_name}"
    db.commit()
    db.refresh(db_doc)

    # 3. Generate SAS URL
    sas_url = generate_sas_url(
        container_name="medical-documents",
        blob_name=db_doc.blob_key,
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        account_key=settings.AZURE_STORAGE_KEY
    )

    # 4. Return document info + SAS URL
    return {
        "id": db_doc.id,
        "patient_id": db_doc.patient_id,
        "file_name": db_doc.file_name,
        "blob_key": db_doc.blob_key,
        "upload_status": db_doc.upload_status,
        "uploaded_at": db_doc.uploaded_at,
        "sas_url": sas_url
    }

#------------------------------ After frontend uploads, it calls /confirm-upload to mark as uploaded and trigger DI -----------------------------

# -----------------------------
# Confirm upload with async DI
# -----------------------------

@router.post("/{document_id}/confirm-upload", response_model=schemas.MedicalDocumentRead)
def confirm_upload(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient_or_409),
):
    # Fetch document and ensure ownership
    db_doc = crud_medical_documents.get_medical_document(db, document_id)
    if not db_doc or db_doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Mark as uploaded
    db_doc.upload_status = "uploaded"
    db.commit()
    db.refresh(db_doc)

    # Launch DI analysis in background
    background_tasks.add_task(run_document_intelligence, db_doc.id, db_doc.blob_key)

    return db_doc

def run_document_intelligence(document_id: int, blob_key: str):
    """
    Runs Document Intelligence asynchronously and stores results in DB.
    Safe for FastAPI BackgroundTasks.
    """
    try:
        # Use a context manager for session
        with database.SessionLocal() as db:
            blob_url = generate_sas_url_for_di(
                container_name="medical-documents",
                blob_name=blob_key,
                account_name=settings.AZURE_STORAGE_ACCOUNT,
                account_key=settings.AZURE_STORAGE_KEY
            )
            print(f"[DI] Analyzing document {document_id} at {blob_url}")

            # Call DI SDK
            # raw_json, summary_text, confidence_score = analyze_document(blob_url)
            raw_json = analyze_document(blob_url)

            # Save DI results
            now = datetime.now(timezone.utc)
            di_record = DocumentIntelligence(
                document_id=document_id,
                status="completed",
                raw_result=raw_json,
                # summary_text=summary_text,
                # confidence_score=confidence_score,
                created_at=now,
                updated_at=now
            )
            db.add(di_record)
            db.commit()
            db.refresh(di_record)

    except Exception as e:
        # Log error
        print(f"[DI ERROR] Document {document_id} failed analysis: {e}")

        # Optional: mark DI as failed in DB
        try:
            with database.SessionLocal() as db:
                db_doc = db.query(DocumentIntelligence).filter_by(document_id=document_id).first()
                if db_doc:
                    db_doc.status = "failed"
                    db_doc.updated_at = datetime.now(timezone.utc)
                    db.commit()
        except SQLAlchemyError as db_err:
            print(f"[DB ERROR] Could not mark document {document_id} as failed: {db_err}")


# ----------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------
# Get single document
# -----------------------------
@router.get("/{document_id}", response_model=schemas.MedicalDocumentRead)
def read_medical_document(
    document_id: int,
    current_patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    db_doc = crud_medical_documents.get_medical_document(db, document_id)
    if not db_doc or db_doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc


# -----------------------------
# List current patient's documents
# -----------------------------
@router.get("/", response_model=List[schemas.MedicalDocumentRead])
def list_my_documents(
    current_patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    return crud_medical_documents.list_medical_documents(db, patient_id=current_patient.id)


# -----------------------------
# Delete document
# -----------------------------
@router.delete("/{document_id}", status_code=204)
def delete_medical_document(
    document_id: int,
    current_patient: Patient = Depends(get_current_patient_or_409),
    db: Session = Depends(get_db)
):
    db_doc = crud_medical_documents.get_medical_document(db, document_id)
    if not db_doc or db_doc.patient_id != current_patient.id:
        raise HTTPException(status_code=404, detail="Document not found")
    crud_medical_documents.delete_medical_document(db, document_id)
    return None
