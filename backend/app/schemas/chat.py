from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Schemas
class ChatQuery(BaseModel):
    question: str = Field(..., min_length=1)
    language: Optional[str] = "en"

# Response Schemas
class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    relevance_score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    response_time: float
    language: str

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
