"""
Database initialization script
Creates all tables including analytics tables
"""

from app.database import engine, Base
from app.models.user import User
from app.models.document import Document
from app.models.analytics import QueryLog, UsageStats

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - documents")
    print("  - query_logs")
    print("  - usage_stats")

if __name__ == "__main__":
    init_db()
