from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import UsageOverview, UsageGraphData, TopTopics
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.services.analytics import get_usage_overview, get_usage_graph_data, get_top_topics

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])
security = HTTPBearer()

@router.get("/overview", response_model=UsageOverview)
async def get_overview(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get overall usage statistics for the authenticated user
    """
    user = await get_current_user(credentials, db)
    stats = get_usage_overview(db, user.id)
    return stats

@router.get("/usage-graph", response_model=UsageGraphData)
async def get_usage_graph(
    period: str = "daily",
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get usage data for graphs (daily or weekly)
    """
    user = await get_current_user(credentials, db)
    data_points = get_usage_graph_data(db, user.id, period)
    
    return {
        "data_points": data_points,
        "period": period
    }

@router.get("/top-topics", response_model=TopTopics)
async def get_top_topics_route(
    limit: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get most queried topics
    """
    user = await get_current_user(credentials, db)
    topics = get_top_topics(db, user.id, limit)
    
    return {"topics": topics}
