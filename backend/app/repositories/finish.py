"""
Finish repository for managing reusable motor and blade finishes.
"""
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class FinishesRepository(BaseRepository):
    collection_name = "finishes"
    id_field = "finish_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_all(
        self, finish_type: Optional[str] = None, is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if finish_type:
            query["type"] = finish_type
        if is_active is not None:
            query["is_active"] = is_active
        cursor = self.collection.find(query).sort("sort_order", 1)
        return await cursor.to_list(length=1000)

    async def find_by_id(self, finish_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": finish_id})

    async def find_by_name_and_type(self, name: str, finish_type: str) -> Optional[Dict[str, Any]]:
        candidates = await self.collection.find({"type": finish_type}).to_list(length=1000)
        target = name.strip().lower()
        for item in candidates:
            if item.get("name", "").strip().lower() == target:
                return item
        return None

    async def find_by_ids(self, finish_ids: List[str]) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"finish_id": {"$in": finish_ids}, "is_active": True})
        return await cursor.to_list(length=len(finish_ids) or 1)

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        eid = data.get("finish_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def update(self, finish_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        await self.collection.update_one({"_id": finish_id}, {"$set": updates})
        return await self.find_by_id(finish_id)

    async def deactivate(self, finish_id: str) -> Optional[Dict[str, Any]]:
        return await self.update(finish_id, {"is_active": False})

    async def upsert_by_id(self, data: Dict[str, Any]) -> None:
        eid = data["finish_id"]
        data = dict(data)
        data["_id"] = eid
        await self.collection.update_one({"_id": eid}, {"$set": data}, upsert=True)
