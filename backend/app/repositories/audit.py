"""
Audit log repository for tracking system and administrative activities.
"""
import uuid
from typing import Any, Dict, List, Optional
from backend.app.repositories.base import BaseRepository, utc_now


class AuditLogsRepository(BaseRepository):
    def __init__(self):
        super().__init__("audit_logs")

    def log(self, action: str, target_entity: str, target_id: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record system action without storing admin identity."""
        entry = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "target_entity": target_entity,
            "target_id": target_id,
            "details": details or {},
            "created_at": utc_now(),
        }
        self.collection.insert_one(entry)
        return entry

    def find_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self.collection.find({}).sort("created_at", -1).limit(limit))


audit_repo = AuditLogsRepository()
