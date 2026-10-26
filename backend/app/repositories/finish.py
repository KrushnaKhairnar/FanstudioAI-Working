"""
Finish repository for managing reusable motor and blade finishes.
"""
from typing import Any, Dict, List, Optional
from backend.app.repositories.base import BaseRepository, utc_now


class FinishesRepository(BaseRepository):
    def __init__(self):
        super().__init__("finishes")

    def find_all(self, finish_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if finish_type:
            query["type"] = finish_type
        if is_active is not None:
            query["is_active"] = is_active
        return list(self.collection.find(query).sort("sort_order", 1))

    def find_by_id(self, finish_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"finish_id": finish_id})

    def find_by_name_and_type(self, name: str, finish_type: str) -> Optional[Dict[str, Any]]:
        candidates = list(self.collection.find({"type": finish_type}))
        target = name.strip().lower()
        for item in candidates:
            if item.get("name", "").strip().lower() == target:
                return item
        return None

    def find_by_ids(self, finish_ids: List[str]) -> List[Dict[str, Any]]:
        return list(self.collection.find({"finish_id": {"$in": finish_ids}, "is_active": True}))

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        self.collection.insert_one(data)
        return data

    def update(self, finish_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        self.collection.update_one({"finish_id": finish_id}, {"$set": updates})
        return self.find_by_id(finish_id)

    def deactivate(self, finish_id: str) -> Optional[Dict[str, Any]]:
        return self.update(finish_id, {"is_active": False})


finishes_repo = FinishesRepository()
