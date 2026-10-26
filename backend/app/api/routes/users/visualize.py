"""
User Visualization Orchestration Router.
Implements the AI Job State Machine (QUEUED -> PROCESSING -> SUCCESS | FAILED)
and composites ceiling fans into customer room photographs.
"""
import asyncio
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import cv2
from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.deps import get_db
from app.repositories import (
    ProductsRepository,
    VariantsRepository,
    FinishesRepository,
    AiJobsRepository,
    RoomsRepository,
    VisualizationResultsRepository,
)
from app.services.image_processing import (
    ROOMS_DIR,
    analyze_room_geometry,
)
from app.services.perspective_lighting import (
    transform_and_composite_fan,
)
from app.core.config import settings

router = APIRouter(prefix="/api/users/visualize", tags=["User AI Visualization"])

VISUALIZATIONS_DIR = os.path.join(settings.DATA_DIR, "visualizations")
os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)


class VisualizationRequest(BaseModel):
    product_id: str = Field(..., description="UUID of fan product")
    variant_id: str = Field(..., description="UUID of explicit variant")
    room_id: Optional[str] = Field(None, description="UUID of preprocessed room upload")
    room_image_url: Optional[str] = Field(None, description="Direct URL of room image")
    scale_factor: float = Field(1.0, ge=0.4, le=2.5, description="Interactive fan size slider [0.4 - 2.5]")
    anchor_x: Optional[float] = Field(None, ge=0.0, le=1.0, description="Interactive X coordinate [0.0 - 1.0]")
    anchor_y: Optional[float] = Field(None, ge=0.0, le=1.0, description="Interactive Y coordinate [0.0 - 1.0]")
    rotation_deg: float = Field(0.0, ge=-360.0, le=360.0, description="Interactive rotation angle in degrees")
    perspective_pitch: float = Field(0.0, ge=-45.0, le=45.0, description="Ceiling pitch angle in degrees")
    apply_lighting: bool = Field(True, description="Harmonize ambient room lighting and temperature")
    apply_shadow: bool = Field(True, description="Synthesize soft ceiling drop-shadow")


class VisualizationJobResponse(BaseModel):
    job_id: str
    status: str
    product_id: str
    variant_id: str
    result_url: Optional[str] = None
    render_time_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def _get_or_create_variant_cutout(
    variant: Dict[str, Any],
    product: Dict[str, Any],
    motor_finish: Dict[str, Any],
    blade_finish: Dict[str, Any],
    size=600,
) -> np.ndarray:
    """Retrieves or generates a 4-channel RGBA fan cutout matching the variant finishes."""
    transparent_url = variant.get("transparent_image_url")
    if transparent_url and os.path.exists(transparent_url):
        loaded = cv2.imread(transparent_url, cv2.IMREAD_UNCHANGED)
        if loaded is not None and loaded.shape[2] == 4:
            return loaded

    def hex_to_bgr(hex_code: str, default: Tuple[int, int, int]):
        hex_clean = hex_code.strip("#") if hex_code else ""
        if len(hex_clean) == 6:
            r = int(hex_clean[0:2], 16)
            g = int(hex_clean[2:4], 16)
            b = int(hex_clean[4:6], 16)
            return (b, g, r)
        return default

    motor_bgr = hex_to_bgr(motor_finish.get("color_code", "#202020"), (35, 35, 35))
    blade_bgr = hex_to_bgr(blade_finish.get("color_code", "#4A3525"), (45, 65, 110))

    specs = product.get("specifications", {})
    blade_count = specs.get("blade_count", 3)

    fan_rgba = np.zeros((size, size, 4), dtype=np.uint8)
    center = (size // 2, size // 2)

    motor_radius = int(size * 0.13)
    cv2.circle(fan_rgba, center, motor_radius, (*motor_bgr, 255), thickness=-1)
    cv2.circle(fan_rgba, center, int(motor_radius * 0.85), (int(motor_bgr[0]*1.15), int(motor_bgr[1]*1.15), int(motor_bgr[2]*1.15), 255), thickness=-1)

    blade_len = int(size * 0.40)
    blade_thickness = int(size * 0.08)
    angle_step = 360.0 / float(blade_count)

    for i in range(blade_count):
        deg = i * angle_step
        rad = np.radians(deg)
        x_end = int(center[0] + blade_len * np.cos(rad))
        y_end = int(center[1] + blade_len * np.sin(rad))
        cv2.line(fan_rgba, center, (x_end, y_end), (*blade_bgr, 255), thickness=blade_thickness)

    cv2.circle(fan_rgba, center, motor_radius, (*motor_bgr, 255), thickness=-1)
    cv2.circle(fan_rgba, center, int(motor_radius * 0.4), (20, 20, 20, 255), thickness=-1)
    fan_rgba[:, :, 3] = cv2.GaussianBlur(fan_rgba[:, :, 3], (5, 5), 0)
    return fan_rgba


def _load_room_bgr(room_id: Optional[str]) -> Tuple[Any, Dict[str, Any]]:
    """Load room image and analysis; returns (room_bgr, room_analysis)."""
    room_bgr = None
    room_analysis: Dict[str, Any] = {}

    if room_id:
        local_path = os.path.join(ROOMS_DIR, f"{room_id}.jpg")
        if os.path.exists(local_path):
            room_bgr = cv2.imread(local_path)

    if room_bgr is None:
        default_path = os.path.join(ROOMS_DIR, "default_bedroom.jpg")
        if os.path.exists(default_path):
            room_bgr = cv2.imread(default_path)
        else:
            room_bgr = np.zeros((720, 1080, 3), dtype=np.uint8)
            room_bgr[0:240, :] = [238, 242, 246]
            room_bgr[240:720, :] = [185, 195, 205]
            cv2.imwrite(default_path, room_bgr)
        room_analysis = analyze_room_geometry(room_bgr)

    return room_bgr, room_analysis


def _render_visualization(
    payload: VisualizationRequest,
    product: Dict[str, Any],
    variant: Dict[str, Any],
    motor_finish: Dict[str, Any],
    blade_finish: Dict[str, Any],
    room_analysis: Dict[str, Any],
    room_id: Optional[str],
) -> Tuple[Any, Dict[str, Any], str, str]:
    """Blocking render pipeline: composite fan into room and write result JPEG."""
    room_bgr, loaded_analysis = _load_room_bgr(room_id)
    if not room_analysis:
        room_analysis = loaded_analysis

    anchor_x = payload.anchor_x if payload.anchor_x is not None else room_analysis.get("ceiling_center_x", 0.50)
    anchor_y = payload.anchor_y if payload.anchor_y is not None else room_analysis.get("ceiling_center_y", 0.24)

    ambient_brightness = float(room_analysis.get("ambient_brightness", 0.70))
    color_temp_kelvin = int(room_analysis.get("color_temp_kelvin", 4500))

    fan_rgba = _get_or_create_variant_cutout(variant, product, motor_finish, blade_finish)

    composite_bgr, meta = transform_and_composite_fan(
        room_bgr=room_bgr,
        fan_rgba=fan_rgba,
        anchor_x_ratio=anchor_x,
        anchor_y_ratio=anchor_y,
        scale_factor=payload.scale_factor,
        rotation_deg=payload.rotation_deg,
        perspective_pitch=payload.perspective_pitch,
        ambient_brightness=ambient_brightness,
        color_temp_kelvin=color_temp_kelvin,
        apply_lighting=payload.apply_lighting,
        apply_shadow=payload.apply_shadow,
    )

    result_id = str(uuid.uuid4())
    result_filename = f"{result_id}.jpg"
    result_filepath = os.path.join(VISUALIZATIONS_DIR, result_filename)
    cv2.imwrite(result_filepath, composite_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])

    result_url = f"/api/static/visualizations/{result_filename}"
    return composite_bgr, meta, result_id, result_url


@router.post("", response_model=VisualizationJobResponse, status_code=status.HTTP_201_CREATED)
async def create_visualization_job(
    payload: VisualizationRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Main AI Room Visualization endpoint.
    Executes the job state machine (QUEUED -> PROCESSING -> SUCCESS / FAILED)
    and composites the selected fan variant into the room photo.
    """
    products_repo = ProductsRepository(db)
    variants_repo = VariantsRepository(db)
    finishes_repo = FinishesRepository(db)
    rooms_repo = RoomsRepository(db)
    ai_jobs_repo = AiJobsRepository(db)
    vis_results_repo = VisualizationResultsRepository(db)

    start_time = time.time()
    job_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    job_doc = {
        "job_id": job_id,
        "status": "QUEUED",
        "product_id": payload.product_id,
        "variant_id": payload.variant_id,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    await ai_jobs_repo.create_job(job_doc)

    await ai_jobs_repo.update_status(job_id, "PROCESSING")

    try:
        product = await products_repo.find_by_id(payload.product_id)
        if not product or product.get("status") != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not active")

        variant = await variants_repo.find_by_id(payload.variant_id)
        if not variant or not variant.get("is_active", True) or variant.get("product_id") != payload.product_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected variant is not valid for this product")

        room_analysis: Dict[str, Any] = {}
        if payload.room_id:
            room_record = await rooms_repo.find_by_id(payload.room_id)
            if room_record:
                room_analysis = room_record.get("analysis", {})

        motor_finish = await finishes_repo.find_by_id(variant["motor_finish_id"]) or {}
        blade_finish = await finishes_repo.find_by_id(variant["blade_finish_id"]) or {}

        _, meta, result_id, result_url = await asyncio.to_thread(
            _render_visualization,
            payload,
            product,
            variant,
            motor_finish,
            blade_finish,
            room_analysis,
            payload.room_id,
        )

        render_time = round((time.time() - start_time) * 1000, 2)

        await ai_jobs_repo.update_job(job_id, {
            "status": "SUCCESS",
            "result_id": result_id,
            "result_url": result_url,
            "render_time_ms": render_time,
            "metadata": meta,
        })

        await vis_results_repo.insert({
            "result_id": result_id,
            "job_id": job_id,
            "product_id": payload.product_id,
            "variant_id": payload.variant_id,
            "result_url": result_url,
            "metadata": meta,
        })

        return VisualizationJobResponse(
            job_id=job_id,
            status="SUCCESS",
            product_id=payload.product_id,
            variant_id=payload.variant_id,
            result_url=result_url,
            render_time_ms=render_time,
            metadata=meta,
        )

    except HTTPException:
        await ai_jobs_repo.update_status(job_id, "FAILED", error="Validation error")
        raise
    except Exception as e:
        await ai_jobs_repo.update_status(job_id, "FAILED", error=str(e))
        return VisualizationJobResponse(
            job_id=job_id,
            status="FAILED",
            product_id=payload.product_id,
            variant_id=payload.variant_id,
            error=str(e),
        )


@router.get("/jobs/{job_id}", response_model=VisualizationJobResponse)
async def get_visualization_job(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Query job status and rendered result."""
    ai_jobs_repo = AiJobsRepository(db)
    job = await ai_jobs_repo.find_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )
    return VisualizationJobResponse(**job)


@router.get("/results/{result_id}")
async def get_visualization_result(result_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Retrieve rendered visualization result metadata and download link."""
    vis_results_repo = VisualizationResultsRepository(db)
    doc = await vis_results_repo.find_by_id(result_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visualization result '{result_id}' not found.",
        )
    return {
        "result_id": doc["result_id"],
        "job_id": doc.get("job_id"),
        "product_id": doc.get("product_id"),
        "variant_id": doc.get("variant_id"),
        "result_url": doc.get("result_url"),
        "metadata": doc.get("metadata"),
        "created_at": doc.get("created_at"),
    }
