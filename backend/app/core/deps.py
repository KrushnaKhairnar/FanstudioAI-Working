"""
Core dependencies for FastAPI routes.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_db as _get_db


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency providing the active Motor database."""
    return _get_db()
