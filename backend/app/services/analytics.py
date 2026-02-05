from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analytics import QueryLog, UsageStats
from app.models.document import Document
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def log_query(
    db: Session,
    user_id: int,
    question: str,
    answer: str,
    response_time: float,
    token_count: int = None,
    language: str = "en"
):
    """Log a query for analytics"""
    query_log = QueryLog(
        user_id=user_id,
        question=question,
        answer=answer,
        response_time=response_time,
        token_count=token_count,
        language=language
    )
    db.add(query_log)
    db.commit()

def get_usage_overview(db: Session, user_id: int) -> Dict:
    """Get overall usage statistics for a user"""
    total_documents = db.query(Document).filter(
        Document.user_id == user_id
    ).count()
    
    total_queries = db.query(QueryLog).filter(
        QueryLog.user_id == user_id
    ).count()
    
    total_tokens = db.query(func.sum(QueryLog.token_count)).filter(
        QueryLog.user_id == user_id
    ).scalar() or 0
    
    avg_response_time = db.query(func.avg(QueryLog.response_time)).filter(
        QueryLog.user_id == user_id
    ).scalar() or 0.0
    
    return {
        "total_documents": total_documents,
        "total_queries": total_queries,
        "total_tokens": int(total_tokens),
        "avg_response_time": float(avg_response_time)
    }

def get_usage_graph_data(db: Session, user_id: int, period: str = "daily") -> List[Dict]:
    """Get usage data for graphs"""
    if period == "daily":
        days = 7
    else:  # weekly
        days = 30
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query logs grouped by date
    query_data = db.query(
        func.date(QueryLog.timestamp).label("date"),
        func.count(QueryLog.id).label("queries")
    ).filter(
        QueryLog.user_id == user_id,
        QueryLog.timestamp >= start_date
    ).group_by(func.date(QueryLog.timestamp)).all()
    
    # Convert to list of dicts
    data_points = []
    for item in query_data:
        # Handle both string (SQLite) and date object (PostgreSQL)
        date_str = item.date if isinstance(item.date, str) else item.date.strftime("%Y-%m-%d")
        data_points.append({
            "date": date_str,
            "queries": item.queries,
            "documents": 0  # Can be enhanced to track daily uploads
        })
    
    return data_points

def get_top_topics(db: Session, user_id: int, limit: int = 5) -> List[Dict]:
    """Extract top queried topics (simplified - extracts keywords)"""
    queries = db.query(QueryLog.question).filter(
        QueryLog.user_id == user_id
    ).all()
    
    # Simple keyword extraction (can be enhanced with NLP)
    from collections import Counter
    import re
    
    words = []
    for query in queries:
        # Extract words longer than 4 characters
        question_words = re.findall(r'\b\w{5,}\b', query.question.lower())
        words.extend(question_words)
    
    # Get most common
    common_words = Counter(words).most_common(limit)
    
    topics = [
        {"topic": word, "count": count}
        for word, count in common_words
    ]
    
    return topics

def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation)"""
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4
