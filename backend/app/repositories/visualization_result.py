"""
Visualization results repository.
"""
from typing import Any, Dict, Optional
from app.repositories.base import BaseRepository, utc_now


class VisualizationResultsRepository(BaseRepository):
    def __init__(self):
        super().__init__("visualization_results")

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("created_at", utc_now())
        self.collection.insert_one(data)
        return data

    def find_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"result_id": result_id})


vis_results_repo = VisualizationResultsRepository()
