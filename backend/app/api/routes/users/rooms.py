"""
User Room Upload & Computer Vision Preprocessing Router.
Accepts user room photos, runs OpenCV geometric and ambient lighting analysis,
and stores preprocessed images for AI ceiling fan visualization compositing.
"""
import asyncio
import uuid
import base64
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.deps import get_db
from app.repositories import RoomsRepository
from app.services.image_processing import (
    validate_and_decode_image,
    analyze_room_geometry,
    save_processed_room,
)

router = APIRouter(prefix="/api/users/rooms", tags=["User Room Upload & Preprocessing"])


class RoomAnalysisOutput(BaseModel):
    ceiling_center_x: float = Field(0.50, description="Normalized X coordinate of ceiling anchor")
    ceiling_center_y: float = Field(0.24, description="Normalized Y coordinate of ceiling anchor")
    ambient_brightness: float = Field(0.5, description="Ambient room brightness [0.0 - 1.0]")
    color_temp_kelvin: int = Field(4500, description="Estimated ambient color temperature in Kelvin")
    ceiling_polygon: List[List[float]] = Field([], description="Detected ceiling boundary polygon")


class RoomUploadResponse(BaseModel):
    room_id: str
    image_url: str
    width: int
    height: int
    analysis: RoomAnalysisOutput
    message: str = "Room photo successfully uploaded and preprocessed."


class Base64UploadRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image string")
    filename: Optional[str] = "uploaded_room.jpg"


@router.post("/upload", response_model=RoomUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_room_file(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Accepts multipart room photo upload (JPG, PNG, WEBP, max 10MB).
    Runs OpenCV preprocessing: auto-rotation, downsampling, and ceiling plane analysis.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        cv_img, meta = await asyncio.to_thread(validate_and_decode_image, contents)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    analysis = await asyncio.to_thread(analyze_room_geometry, cv_img)
    room_id = str(uuid.uuid4())
    img_url = await asyncio.to_thread(save_processed_room, room_id, cv_img)

    now_iso = datetime.now(timezone.utc).isoformat()
    room_doc = {
        "room_id": room_id,
        "image_url": img_url,
        "original_filename": file.filename,
        "width": meta["width"],
        "height": meta["height"],
        "analysis": analysis,
        "created_at": now_iso,
    }
    rooms_repo = RoomsRepository(db)
    await rooms_repo.insert(room_doc)

    return RoomUploadResponse(
        room_id=room_id,
        image_url=img_url,
        width=meta["width"],
        height=meta["height"],
        analysis=RoomAnalysisOutput(**analysis),
    )


@router.post("/upload-base64", response_model=RoomUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_room_base64(
    payload: Base64UploadRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Accepts base64 room photo data URI or raw base64 string."""
    raw_str = payload.image_base64
    if "," in raw_str:
        raw_str = raw_str.split(",", 1)[1]

    try:
        raw_bytes = base64.b64decode(raw_str)
        cv_img, meta = await asyncio.to_thread(validate_and_decode_image, raw_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process base64 image: {str(e)}",
        )

    analysis = await asyncio.to_thread(analyze_room_geometry, cv_img)
    room_id = str(uuid.uuid4())
    img_url = await asyncio.to_thread(save_processed_room, room_id, cv_img)

    now_iso = datetime.now(timezone.utc).isoformat()
    room_doc = {
        "room_id": room_id,
        "image_url": img_url,
        "original_filename": payload.filename,
        "width": meta["width"],
        "height": meta["height"],
        "analysis": analysis,
        "created_at": now_iso,
    }
    rooms_repo = RoomsRepository(db)
    await rooms_repo.insert(room_doc)

    return RoomUploadResponse(
        room_id=room_id,
        image_url=img_url,
        width=meta["width"],
        height=meta["height"],
        analysis=RoomAnalysisOutput(**analysis),
    )


@router.get("/{room_id}", response_model=RoomUploadResponse)
async def get_room(room_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Retrieve preprocessed room photo information and geometric analysis."""
    rooms_repo = RoomsRepository(db)
    doc = await rooms_repo.find_by_id(room_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID '{room_id}' not found.",
        )

    return RoomUploadResponse(
        room_id=doc["room_id"],
        image_url=doc["image_url"],
        width=doc["width"],
        height=doc["height"],
        analysis=RoomAnalysisOutput(**doc["analysis"]),
    )
