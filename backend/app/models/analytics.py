from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.sql import func
from app.database import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    response_time = Column(Float, nullable=True)  # in seconds
    token_count = Column(Integer, nullable=True)  # estimated tokens
    language = Column(String, default="en")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QueryLog user={self.user_id} at {self.timestamp}>"

class UsageStats(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_queries = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<UsageStats user={self.user_id} date={self.date}>"
