"""
Audit log repository for tracking system and administrative activities.
"""
import uuid
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class AuditLogsRepository(BaseRepository):
    collection_name = "audit_logs"
    id_field = "log_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def log(
        self,
        action: str,
        target_entity: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record system action without storing admin identity."""
        log_id = str(uuid.uuid4())
        entry = {
            "_id": log_id,
            "log_id": log_id,
            "action": action,
            "target_entity": target_entity,
            "target_id": target_id,
            "details": details or {},
            "created_at": utc_now(),
        }
        await self.collection.insert_one(entry)
        return entry

    async def find_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.collection.find({}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
