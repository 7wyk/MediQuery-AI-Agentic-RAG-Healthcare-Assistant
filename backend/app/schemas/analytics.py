from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

# Response Schemas
class UsageOverview(BaseModel):
    total_documents: int
    total_queries: int
    total_tokens: int
    avg_response_time: float

class UsageDataPoint(BaseModel):
    date: str
    queries: int
    documents: int

class UsageGraphData(BaseModel):
    data_points: List[UsageDataPoint]
    period: str  # "daily" or "weekly"

class TopicData(BaseModel):
    topic: str
    count: int

class TopTopics(BaseModel):
    topics: List[TopicData]
