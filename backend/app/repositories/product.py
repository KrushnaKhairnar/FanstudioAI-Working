"""
Product repository for managing fan catalog records.
"""
from typing import Any, Dict, List, Optional
from backend.app.repositories.base import BaseRepository, utc_now


class ProductsRepository(BaseRepository):
    def __init__(self):
        super().__init__("products")

    def find_all(self, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        query = {"status": status} if status else {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return list(cursor)

    def find_by_status(self, status: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.collection.find({"status": status}).skip(skip).limit(limit))

    def find_active(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.collection.find({"status": "active"}).skip(skip).limit(limit))

    def find_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"product_id": product_id})

    def find_by_code(self, product_code: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"product_code": product_code})

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        data.setdefault("updated_at", utc_now())
        self.collection.insert_one(data)
        return data

    def update(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        self.collection.update_one({"product_id": product_id}, {"$set": updates})
        return self.find_by_id(product_id)

    def soft_delete_or_deactivate(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.update(product_id, {"status": "inactive"})

    def restore(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.update(product_id, {"status": "active"})


products_repo = ProductsRepository()
