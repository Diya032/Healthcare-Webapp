from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from app.models.models import DocumentIntelligence
from app.schemas.schemas_blob_di import DocumentIntelligenceCreate, DocumentIntelligenceUpdate

# Create a new DI record
def create_document_intelligence(db: Session, di_in: DocumentIntelligenceCreate) -> DocumentIntelligence:
    db_di = DocumentIntelligence(
        document_id=di_in.document_id,
        status=di_in.status or "processing",
        raw_result=di_in.raw_result,
        # summary_text=di_in.summary_text,
        # confidence_score=di_in.confidence_score,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_di)
    db.commit()
    db.refresh(db_di)
    return db_di

# Get DI by document_id
def get_document_intelligence(db: Session, document_id: int) -> Optional[DocumentIntelligence]:
    return db.query(DocumentIntelligence).filter(DocumentIntelligence.document_id == document_id).first()

# Update DI record
def update_document_intelligence(db: Session, document_id: int, di_in: DocumentIntelligenceUpdate) -> Optional[DocumentIntelligence]:
    db_di = get_document_intelligence(db, document_id)
    if not db_di:
        return None
    for field, value in di_in.model_dump(exclude_unset=True).items():
        setattr(db_di, field, value)
    db_di.updated_at = datetime.now()
    db.commit()
    db.refresh(db_di)
    return db_di

# Delete DI record (usually cascade from MedicalDocument)
def delete_document_intelligence(db: Session, document_id: int) -> bool:
    db_di = get_document_intelligence(db, document_id)
    if not db_di:
        return False
    db.delete(db_di)
    db.commit()
    return True


