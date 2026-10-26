"""
Core dependencies for FastAPI routes.
"""
from app.db.mongo import db_manager, MongoDBManager


def get_db() -> MongoDBManager:
    """Dependency providing active database manager."""
    return db_manager
