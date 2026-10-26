"""
Admin Finish Management Router.
Full CRUD, color styling, sort ordering, and soft-deactivation.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.repositories import (
    finishes_repo,
    audit_repo,
)
from backend.app.models.finish import (
    Finish,
    FinishCreate,
    FinishUpdate,
)

router = APIRouter(prefix="/api/admin/finishes", tags=["Admin Finishes"])


class FinishStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Target active status for the finish")


@router.get("", response_model=List[Finish])
def list_finishes(
    finish_type: Optional[Literal["motor", "blade"]] = Query(None, alias="type"),
    is_active: Optional[bool] = Query(None),
):
    """List all finishes with optional type (motor/blade) and status filtering."""
    finishes = finishes_repo.find_all(finish_type=finish_type, is_active=is_active)
    return [Finish(**f) for f in finishes]


@router.get("/{finish_id}", response_model=Finish)
def get_finish(finish_id: str):
    """Retrieve single finish by UUID."""
    finish = finishes_repo.find_by_id(finish_id)
    if not finish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finish with ID '{finish_id}' not found.",
        )
    return Finish(**finish)


@router.post("", response_model=Finish, status_code=status.HTTP_201_CREATED)
def create_finish(payload: FinishCreate):
    """Create a new reusable motor or blade finish."""
    existing = finishes_repo.find_by_name_and_type(payload.name, payload.type)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A {payload.type} finish named '{payload.name}' already exists.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    new_id = str(uuid.uuid4())
    doc = payload.model_dump()
    doc["finish_id"] = new_id
    doc["created_at"] = now_iso
    doc["updated_at"] = now_iso

    created = finishes_repo.insert(doc)

    audit_repo.log(
        action="CREATE_FINISH",
        target_entity="finish",
        target_id=new_id,
        details={"name": payload.name, "type": payload.type},
    )

    return Finish(**created)


@router.put("/{finish_id}", response_model=Finish)
def update_finish(finish_id: str, payload: FinishUpdate):
    """Update finish details, swatch image, color code, or sort order."""
    existing = finishes_repo.find_by_id(finish_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finish with ID '{finish_id}' not found.",
        )

    target_name = payload.name or existing.get("name")
    target_type = payload.type or existing.get("type")
    if (payload.name and payload.name != existing.get("name")) or (payload.type and payload.type != existing.get("type")):
        duplicate = finishes_repo.find_by_name_and_type(target_name, target_type)
        if duplicate and duplicate.get("finish_id") != finish_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another {target_type} finish with name '{target_name}' already exists.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = finishes_repo.update(finish_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update finish.")

    audit_repo.log(
        action="UPDATE_FINISH",
        target_entity="finish",
        target_id=finish_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return Finish(**updated)


@router.patch("/{finish_id}/status", response_model=Finish)
def update_finish_status(finish_id: str, payload: FinishStatusUpdate):
    """Activate or deactivate a finish."""
    existing = finishes_repo.find_by_id(finish_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finish with ID '{finish_id}' not found.",
        )

    updated = finishes_repo.update(finish_id, {
        "is_active": payload.is_active,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    audit_repo.log(
        action="UPDATE_FINISH_STATUS",
        target_entity="finish",
        target_id=finish_id,
        details={"previous_active": existing.get("is_active"), "new_active": payload.is_active},
    )

    return Finish(**updated)


@router.delete("/{finish_id}")
def deactivate_finish(finish_id: str):
    """Soft-deactivate finish (sets is_active to False). Never hard deletes if referenced by variants."""
    existing = finishes_repo.find_by_id(finish_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finish with ID '{finish_id}' not found.",
        )

    finishes_repo.update(finish_id, {
        "is_active": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    audit_repo.log(
        action="DEACTIVATE_FINISH",
        target_entity="finish",
        target_id=finish_id,
        details={"name": existing.get("name"), "type": existing.get("type")},
    )

    return {
        "message": f"Finish '{existing.get('name')}' successfully deactivated.",
        "finish_id": finish_id,
        "is_active": False,
    }
