from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.models.models import MedicalDocument
from app.schemas.schemas_blob_di import MedicalDocumentCreate, MedicalDocumentUpdate

# Create a new medical document record
def create_medical_document(db: Session, doc_in: MedicalDocumentCreate) -> MedicalDocument:
    db_doc = MedicalDocument(
        patient_id=doc_in.patient_id,
        file_name=doc_in.file_name,
        content_type=doc_in.content_type,
        upload_status="pending",
        uploaded_at=datetime.now(timezone.utc)
    )
    
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

# Get a document by ID
def get_medical_document(db: Session, document_id: int) -> Optional[MedicalDocument]:
    return db.query(MedicalDocument).filter(MedicalDocument.id == document_id).first()

# List documents (optional filter by patient)
def list_medical_documents(db: Session, patient_id: Optional[int] = None) -> List[MedicalDocument]:
    query = db.query(MedicalDocument)
    if patient_id:
        query = query.filter(MedicalDocument.patient_id == patient_id)
    return query.order_by(MedicalDocument.uploaded_at.desc()).all()

# Update document (e.g., upload status)
def update_medical_document(db: Session, document_id: int, doc_in: MedicalDocumentUpdate) -> Optional[MedicalDocument]:
    db_doc = get_medical_document(db, document_id)
    if not db_doc:
        return None
    for field, value in doc_in.model_dump(exclude_unset=True).items():
        setattr(db_doc, field, value)
    db.commit()
    db.refresh(db_doc)
    return db_doc

# Delete document
def delete_medical_document(db: Session, document_id: int) -> bool:
    db_doc = get_medical_document(db, document_id)
    if not db_doc:
        return False
    db.delete(db_doc)
    db.commit()
    return True


