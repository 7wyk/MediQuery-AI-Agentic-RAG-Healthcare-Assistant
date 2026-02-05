from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    pinecone_namespace = Column(String, nullable=False)  # user-specific namespace
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADING)
    error_message = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Document {self.filename} - {self.status}>"
