"""
AI Job repository for managing room visualization jobs.
"""
from typing import Any, Dict, Optional
from app.repositories.base import BaseRepository, utc_now


class AiJobsRepository(BaseRepository):
    def __init__(self):
        super().__init__("ai_jobs")

    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        job_data.setdefault("status", "QUEUED")
        job_data.setdefault("created_at", utc_now())
        self.collection.insert_one(job_data)
        return job_data

    def find_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"job_id": job_id})

    def update_status(self, job_id: str, status: str, result_id: Optional[str] = None, error: Optional[str] = None) -> Optional[Dict[str, Any]]:
        updates = {"status": status, "updated_at": utc_now()}
        if result_id:
            updates["result_id"] = result_id
        if error:
            updates["error"] = error
        self.collection.update_one({"job_id": job_id}, {"$set": updates})
        return self.find_by_id(job_id)

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        self.collection.update_one({"job_id": job_id}, {"$set": updates})
        return self.find_by_id(job_id)


ai_jobs_repo = AiJobsRepository()
