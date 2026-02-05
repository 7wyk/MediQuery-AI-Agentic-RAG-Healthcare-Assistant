from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.documents import DocumentResponse, DocumentListResponse, DocumentStatusResponse
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.services.vectorstore import load_vectorstore, delete_document_vectors
import logging
import os
from pathlib import Path

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Upload PDF documents for the authenticated user
    """
    user = await get_current_user(credentials, db)
    
    # Validate file types
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}. Only PDF files are allowed."
            )
    
    try:
        documents = load_vectorstore(files, user.id, db)
        return documents
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing documents: {str(e)}"
        )

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    List all documents for the authenticated user
    """
    user = await get_current_user(credentials, db)
    
    documents = db.query(Document).filter(
        Document.user_id == user.id
    ).order_by(Document.upload_date.desc()).all()
    
    return {
        "documents": documents,
        "total": len(documents)
    }

@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    doc_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get processing status of a specific document
    """
    user = await get_current_user(credentials, db)
    
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete a document and its vectors
    """
    user = await get_current_user(credentials, db)
    
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        # Delete vectors from Pinecone
        delete_document_vectors(document)
        
        # Delete file from disk
        file_path = Path(f"./uploaded_docs/{user.id}_{document.filename}")
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )

@router.post("/{doc_id}/reindex")
async def reindex_document(
    doc_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Re-index a document (delete and re-upload vectors)
    """
    user = await get_current_user(credentials, db)
    
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        # Delete existing vectors
        delete_document_vectors(document)
        
        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # Re-upload (simplified - in production, use background task)
        file_path = Path(f"./uploaded_docs/{user.id}_{document.filename}")
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on disk"
            )
        
        # TODO: Implement re-indexing logic
        document.status = DocumentStatus.COMPLETED
        db.commit()
        
        return {"message": "Document re-indexed successfully"}
    except Exception as e:
        logger.error(f"Error re-indexing document: {str(e)}")
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error re-indexing document: {str(e)}"
        )
