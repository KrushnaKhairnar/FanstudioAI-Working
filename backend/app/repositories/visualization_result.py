"""
Visualization results repository.
"""
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class VisualizationResultsRepository(BaseRepository):
    collection_name = "visualization_results"
    id_field = "result_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        eid = data.get("result_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def find_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": result_id})
