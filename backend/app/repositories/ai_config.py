"""
AI Configuration repository for placement, scale, and lighting offsets.
"""
from typing import Any, Dict, Optional
from app.repositories.base import BaseRepository, utc_now


class AiConfigRepository(BaseRepository):
    def __init__(self):
        super().__init__("ai_configurations")

    def find_by_target(self, target_type: str, target_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"target_type": target_type, "target_id": target_id})

    def upsert_config(self, target_type: str, target_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.find_by_target(target_type, target_id)
        config_data["updated_at"] = utc_now()
        if existing:
            self.collection.update_one({"target_type": target_type, "target_id": target_id}, {"$set": config_data})
            return {**existing, **config_data}
        else:
            config_data["target_type"] = target_type
            config_data["target_id"] = target_id
            config_data.setdefault("created_at", utc_now())
            self.collection.insert_one(config_data)
            return config_data


ai_config_repo = AiConfigRepository()
