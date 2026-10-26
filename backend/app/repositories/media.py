"""
Media repository for managing fan imagery, cutouts, and renders.
"""
from typing import Any, Dict, List, Optional
from app.repositories.base import BaseRepository, utc_now


class MediaRepository(BaseRepository):
    def __init__(self):
        super().__init__("product_media")

    def find_by_product(self, product_id: str, variant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"product_id": product_id}
        if variant_id:
            query["variant_id"] = variant_id
        return list(self.collection.find(query).sort("sort_order", 1))

    def find_by_id(self, media_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"media_id": media_id})

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        self.collection.insert_one(data)
        return data

    def update(self, media_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        self.collection.update_one({"media_id": media_id}, {"$set": updates})
        return self.find_by_id(media_id)

    def delete(self, media_id: str) -> bool:
        res = self.collection.delete_one({"media_id": media_id})
        return res.deleted_count > 0 if hasattr(res, "deleted_count") else True


media_repo = MediaRepository()
