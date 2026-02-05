import os
import time
from pathlib import Path
from typing import List
from fastapi import UploadFile
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from sqlalchemy.orm import Session
from app.models.document import Document, DocumentStatus
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Pinecone configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medical-local-384")

# Set Google API key environment variable for other tools might need it
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,  # standard for all-MiniLM-L6-v2
        metric="dotproduct",
        spec=spec
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)

def load_vectorstore(
    uploaded_files: List[UploadFile],
    user_id: int,
    db: Session
) -> List[Document]:
    """
    Load PDFs, chunk, embed, and upsert to Pinecone with user-specific namespace.
    Track documents in database.
    """
    # Use Local Embeddings (Fast, Free, No Rate Limits)
    embed_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    documents = []
    
    # User-specific namespace for document isolation
    namespace = f"user_{user_id}"
    
    for file in uploaded_files:
        # Save file
        save_path = Path(UPLOAD_DIR) / f"{user_id}_{file.filename}"
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        
        # Create document record
        doc = Document(
            user_id=user_id,
            filename=file.filename,
            file_size=save_path.stat().st_size,
            pinecone_namespace=namespace,
            status=DocumentStatus.PROCESSING
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        documents.append(doc)
        
        try:
            # Load and split PDF
            loader = PyPDFLoader(str(save_path))
            pages = loader.load()
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = splitter.split_documents(pages)
            
            # Prepare data for Pinecone
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [
                {
                    **chunk.metadata,
                    "text": chunk.page_content,
                    "filename": file.filename,
                    "user_id": user_id
                }
                for chunk in chunks
            ]
            ids = [f"{doc.id}-{i}" for i in range(len(chunks))]
            
            logger.info(f"Embedding {len(texts)} chunks for {file.filename} using local model...")
            
            # Fast Local Embedding (No rate limits!)
            embeddings = embed_model.embed_documents(texts)
            
            logger.info(f"Uploading to Pinecone namespace: {namespace}...")
            # Upsert to user-specific namespace
            upsert_batch_size = 100
            for i in range(0, len(embeddings), upsert_batch_size):
                batch_ids = ids[i:i+upsert_batch_size]
                batch_embeds = embeddings[i:i+upsert_batch_size]
                batch_metas = metadatas[i:i+upsert_batch_size]
                
                # Ensure we don't have mismatch caused by failed embeddings
                if len(batch_embeds) != len(batch_ids):
                     raise ValueError("Mismatch between embeddings and IDs count")

                index.upsert(
                    vectors=list(zip(batch_ids, batch_embeds, batch_metas)),
                    namespace=namespace
                )
            
            # Update status to completed
            doc.status = DocumentStatus.COMPLETED
            db.commit()
            logger.info(f"✅ Upload complete for {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            db.commit()
    
    return documents

def delete_document_vectors(document: Document):
    """
    Delete document vectors from Pinecone
    """
    try:
        # Delete all vectors with this document ID prefix
        index.delete(
            filter={"filename": document.filename},
            namespace=document.pinecone_namespace
        )
        logger.info(f"Deleted vectors for document {document.filename}")
    except Exception as e:
        # Ignore namespace not found errors, as it means there's nothing to delete
        if "Namespace not found" in str(e) or "404" in str(e):
            logger.warning(f"Namespace/Vector not found during deletion (safe to ignore): {str(e)}")
        else:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise

def get_user_retriever(user_id: int, question: str, top_k: int = 3):
    """
    Get retriever for user-specific documents
    """
    from langchain_core.documents import Document as LCDocument
    
    namespace = f"user_{user_id}"
    embed_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Embed query (Fast & Local)
    embedded_query = embed_model.embed_query(question)
    
    # Query user's namespace
    res = index.query(
        vector=embedded_query,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    
    # Convert to LangChain documents
    docs = [
        LCDocument(
            page_content=match["metadata"].get("text", ""),
            metadata=match["metadata"]
        )
        for match in res["matches"]
    ]
    
    return docs
