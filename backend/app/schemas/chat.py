from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Schemas
class ChatQuery(BaseModel):
    question: str = Field(..., min_length=1)
    language: Optional[str] = "en"
    mode: Optional[str] = Field(default="standard", description="RAG mode: 'standard' or 'agentic'")

# Response Schemas
class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    relevance_score: Optional[float] = None

class AgentMetadata(BaseModel):
    """Metadata from Agentic RAG execution — only present when mode='agentic'."""
    retrieval_attempts: int = 1
    retrieval_refined: bool = False
    documents_retrieved: int = 0
    relevance_score: float = 0.0
    steps: List[str] = []
    fallback_to_standard: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    response_time: float
    language: str
    mode: Optional[str] = "standard"
    agent_metadata: Optional[AgentMetadata] = None

class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    timestamp: datetime
    language: str

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryItem]
    total: int
