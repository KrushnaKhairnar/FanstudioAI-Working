"""
Room repository for preprocessed room photos and ceiling analyses.
"""
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class RoomsRepository(BaseRepository):
    collection_name = "rooms"
    id_field = "room_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        eid = data.get("room_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def find_by_id(self, room_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": room_id})
