"""
Product repository for managing fan catalog records.
"""
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class ProductsRepository(BaseRepository):
    collection_name = "products"
    id_field = "product_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_all(self, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        query = {"status": status} if status else {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_by_status(self, status: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"status": status}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_active(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"status": "active"}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": product_id})

    async def find_by_code(self, product_code: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"product_code": product_code})

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        data.setdefault("updated_at", utc_now())
        eid = data.get("product_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def update(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        await self.collection.update_one({"_id": product_id}, {"$set": updates})
        return await self.find_by_id(product_id)

    async def soft_delete_or_deactivate(self, product_id: str) -> Optional[Dict[str, Any]]:
        return await self.update(product_id, {"status": "inactive"})

    async def restore(self, product_id: str) -> Optional[Dict[str, Any]]:
        return await self.update(product_id, {"status": "active"})

    async def delete(self, product_id: str) -> bool:
        res = await self.collection.delete_one({"_id": product_id})
        return res.deleted_count > 0
