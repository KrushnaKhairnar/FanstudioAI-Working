"""
AI Job repository for managing room visualization jobs.
"""
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository, utc_now


class AiJobsRepository(BaseRepository):
    collection_name = "ai_jobs"
    id_field = "job_id"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        job_data.setdefault("status", "QUEUED")
        job_data.setdefault("created_at", utc_now())
        eid = job_data.get("job_id")
        if eid:
            job_data["_id"] = eid
        await self.collection.insert_one(job_data)
        return job_data

    async def find_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": job_id})

    async def update_status(
        self,
        job_id: str,
        status: str,
        result_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        updates: Dict[str, Any] = {"status": status, "updated_at": utc_now()}
        if result_id:
            updates["result_id"] = result_id
        if error:
            updates["error"] = error
        await self.collection.update_one({"_id": job_id}, {"$set": updates})
        return await self.find_by_id(job_id)

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = utc_now()
        await self.collection.update_one({"_id": job_id}, {"$set": updates})
        return await self.find_by_id(job_id)
