from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentStatus

# Request Schemas
class DocumentUpload(BaseModel):
    pass  # File upload handled by FastAPI UploadFile

# Response Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_date: datetime
    status: DocumentStatus
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

class DocumentStatusResponse(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
