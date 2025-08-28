from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


# Base schema for shared fields
class MedicalDocumentBase(BaseModel):
    file_name: str
    # blob_key: str
    content_type: Optional[str] = None
    # file_size: Optional[int] = None

# -----------------------------
# Input schema (from frontend)
# -----------------------------
class MedicalDocumentUploadIn(MedicalDocumentBase):
    pass   # frontend sends only file_name + content_type

# Schema for creating a new document (upload request) Internal create schema (used in DB + crud)
class MedicalDocumentCreate(MedicalDocumentBase):
    patient_id: int # backend injects this, not required from request
    pass

# Schema for updating upload status or metadata
class MedicalDocumentUpdate(BaseModel):
    upload_status: Optional[str] = None
    # file_size: Optional[int] = None
    content_type: Optional[str] = None

# Schema for returning document info
class MedicalDocumentRead(MedicalDocumentBase):
    id: int
    upload_status: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
        

# -----------------------------
# Upload response schema (frontend)
# -----------------------------
class MedicalDocumentUploadResponse(BaseModel):
    id: int
    patient_id: int
    file_name: str
    blob_key: str
    upload_status: str
    uploaded_at: datetime
    sas_url: str  # short-lived SAS token URL for upload

    class Config:
        orm_mode = True


# -----------------------------Document Intlelligence-----------------------------

# Base schema
class DocumentIntelligenceBase(BaseModel):
    document_id: int
    status: Optional[str] = "processing"
    # summary_text: Optional[str] = None
    # confidence_score: Optional[float] = None

# Schema for creating analysis record
class DocumentIntelligenceCreate(DocumentIntelligenceBase):
    raw_result: Optional[Any] = None  # JSON output from Document Intelligence

# Schema for updating analysis record
class DocumentIntelligenceUpdate(BaseModel):
    status: Optional[str] = None
    raw_result: Optional[Any] = None
    # summary_text: Optional[str] = None
    # confidence_score: Optional[float] = None

# Schema for returning analysis info
class DocumentIntelligenceRead(DocumentIntelligenceBase):
    id: int
    raw_result: Optional[Any] = None
    created_at: datetime
    updated_at: datetime


class DocumentIntelligenceOut(BaseModel):
    document_id: int
    raw_result: Optional[Any] = None
    # summary_text: Optional[str] = None
    # confidence_score: Optional[float] = None
    status: str = "processing"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

