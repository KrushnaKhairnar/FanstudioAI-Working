"""
Variant repository for managing fan motor + blade combinations.
"""
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class VariantsRepository(BaseRepository):
    collection_name = "product_variants"
    id_field = "variant_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_by_product(self, product_id: str, only_active: bool = False) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"product_id": product_id}
        if only_active:
            query["is_active"] = True
        return await self.collection.find(query).to_list(length=1000)

    async def find_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": variant_id})

    async def find_exact(
        self, product_id: str, motor_finish_id: str, blade_finish_id: str
    ) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({
            "product_id": product_id,
            "motor_finish_id": motor_finish_id,
            "blade_finish_id": blade_finish_id,
        })

    async def find_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"sku": sku.strip()})

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        eid = data.get("variant_id")
        if eid:
            data["_id"] = eid
        await self.collection.insert_one(data)
        return data

    async def update(self, variant_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        await self.collection.update_one({"_id": variant_id}, {"$set": updates})
        return await self.find_by_id(variant_id)

    async def set_active(self, variant_id: str, is_active: bool) -> Optional[Dict[str, Any]]:
        return await self.update(variant_id, {"is_active": is_active})
