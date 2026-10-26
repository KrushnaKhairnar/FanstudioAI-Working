"""
AI Configuration repository for placement, scale, and lighting offsets.
"""
from typing import Any, Dict, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class AiConfigRepository(BaseRepository):
    collection_name = "ai_configurations"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_by_target(self, target_type: str, target_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"target_type": target_type, "target_id": target_id})

    async def upsert_config(
        self, target_type: str, target_id: str, config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        existing = await self.find_by_target(target_type, target_id)
        config_data["updated_at"] = utc_now()
        if existing:
            await self.collection.update_one(
                {"target_type": target_type, "target_id": target_id},
                {"$set": config_data},
            )
            return {**existing, **config_data}
        config_data["target_type"] = target_type
        config_data["target_id"] = target_id
        config_data.setdefault("created_at", utc_now())
        eid = config_data.get("config_id") or str(uuid4())
        config_data["config_id"] = eid
        config_data["_id"] = eid
        await self.collection.insert_one(config_data)
        return config_data
