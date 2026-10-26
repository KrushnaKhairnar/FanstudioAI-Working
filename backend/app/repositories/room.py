"""
Room repository for preprocessed room photos and ceiling analyses.
"""
from typing import Any, Dict, Optional
from app.repositories.base import BaseRepository, utc_now


class RoomsRepository(BaseRepository):
    def __init__(self):
        super().__init__("rooms")

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        self.collection.insert_one(data)
        return data

    def find_by_id(self, room_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"room_id": room_id})


rooms_repo = RoomsRepository()
