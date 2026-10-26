"""
Base repository providing common data access primitives.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection


def utc_now() -> str:
    """Current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


class BaseRepository:
    collection_name: str = ""
    id_field: str = "_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self.db[self.collection_name]

    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        return await self.collection.count_documents(query or {})
