"""
Base repository providing common data access primitives.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.app.db.mongo import db_manager


def utc_now() -> str:
    """Current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


class BaseRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def collection(self):
        return getattr(db_manager, self.collection_name)

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        return self.collection.count_documents(query or {}) if hasattr(self.collection, "count_documents") else len(list(self.collection.find(query or {})))
