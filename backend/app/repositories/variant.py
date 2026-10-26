"""
Variant repository for managing fan motor + blade combinations.
"""
from typing import Any, Dict, List, Optional
from app.repositories.base import BaseRepository, utc_now


class VariantsRepository(BaseRepository):
    def __init__(self):
        super().__init__("product_variants")

    def find_by_product(self, product_id: str, only_active: bool = False) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"product_id": product_id}
        if only_active:
            query["is_active"] = True
        return list(self.collection.find(query))

    def find_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"variant_id": variant_id})

    def find_exact(self, product_id: str, motor_finish_id: str, blade_finish_id: str) -> Optional[Dict[str, Any]]:
        """Validate if exact combination is an approved variant."""
        return self.collection.find_one({
            "product_id": product_id,
            "motor_finish_id": motor_finish_id,
            "blade_finish_id": blade_finish_id,
        })

    def find_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"sku": sku.strip()})

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        self.collection.insert_one(data)
        return data

    def update(self, variant_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        self.collection.update_one({"variant_id": variant_id}, {"$set": updates})
        return self.find_by_id(variant_id)

    def set_active(self, variant_id: str, is_active: bool) -> Optional[Dict[str, Any]]:
        return self.update(variant_id, {"is_active": is_active})


variants_repo = VariantsRepository()
