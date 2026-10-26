"""
Media repository for managing fan imagery, cutouts, and renders.
"""
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class MediaRepository(BaseRepository):
    collection_name = "product_media"
    id_field = "media_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_by_product(
        self, product_id: str, variant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"product_id": product_id}
        if variant_id:
            query["variant_id"] = variant_id
        cursor = self.collection.find(query).sort("sort_order", 1)
        return await cursor.to_list(length=1000)

    async def find_by_id(self, media_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": media_id})

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        eid = data.get("media_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def update(self, media_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        await self.collection.update_one({"_id": media_id}, {"$set": updates})
        return await self.find_by_id(media_id)

    async def delete(self, media_id: str) -> bool:
        res = await self.collection.delete_one({"_id": media_id})
        return res.deleted_count > 0
