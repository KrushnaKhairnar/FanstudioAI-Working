"""
AI and Computer Vision Domain Models.
Adheres to Master Development Plan Section 6, 10, and 11:
- AIProductConfiguration
- AIJob (QUEUED -> PROCESSING -> SUCCESS | FAILED | CANCELLED)
- RoomAnalysis (Ceiling polygon, depth, obstacle bounding boxes, placement coordinates)
- GeneratedResult
"""
import uuid
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class AIProductConfiguration(BaseModel):
    product_id: Optional[str] = Field(None, description="UUID of associated fan product")
    variant_id: Optional[str] = Field(None, description="Optional UUID of associated variant")
    enabled: bool = Field(True, description="Whether AI visualization is enabled for this product")
    reference_image_url: Optional[str] = Field(None, description="High-resolution reference image for CV engine")
    transparent_reference_url: Optional[str] = Field(None, description="Alpha-cutout transparent asset")
    transparent_png_url: Optional[str] = Field(None, description="Alias for transparent_reference_url")
    mask_image_url: Optional[str] = Field(None, description="Binary mask for blade & motor geometry")
    mask_url: Optional[str] = Field(None, description="Alias for mask_image_url")
    segmentation_image_url: Optional[str] = Field(None, description="Semantic segmentation reference")
    placement_scale: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Scale factor relative to room ceiling depth")
    default_scale: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Alias for placement_scale")
    placement_offset_x: Optional[float] = Field(0.0, ge=-1.0, le=1.0, description="Horizontal anchor offset")
    placement_offset_y: Optional[float] = Field(0.0, ge=-1.0, le=1.0, description="Vertical anchor offset")
    vertical_offset_ratio: Optional[float] = Field(-0.05, description="Vertical anchor offset ratio")
    rotation_angle: Optional[float] = Field(0.0, ge=-360.0, le=360.0, description="Default rotation angle in degrees")
    blending_mode: Optional[str] = Field("perspective_composite", description="Blending mode for CV engine")
    lighting_adaptation: Optional[bool] = Field(True, description="Whether to apply room lighting color balance")
    generation_prompt: Optional[str] = Field(None, max_length=1000, description="Product-specific diffusion composition prompt")

    def model_post_init(self, __context):
        if not self.transparent_reference_url and self.transparent_png_url:
            self.transparent_reference_url = self.transparent_png_url
        elif not self.transparent_png_url and self.transparent_reference_url:
            self.transparent_png_url = self.transparent_reference_url

        if not self.mask_image_url and self.mask_url:
            self.mask_image_url = self.mask_url
        elif not self.mask_url and self.mask_image_url:
            self.mask_url = self.mask_image_url

        if self.default_scale != 1.0 and self.placement_scale == 1.0:
            self.placement_scale = self.default_scale
        elif self.placement_scale != 1.0 and self.default_scale == 1.0:
            self.default_scale = self.placement_scale


class AIJobCreate(BaseModel):
    product_id: str = Field(..., description="UUID of selected fan product")
    variant_id: str = Field(..., description="UUID of selected explicit variant")
    input_room_image_url: str = Field(..., description="URL or data URI of user's uploaded room image")


class AIJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Primary UUID for generation job")
    status: Literal["QUEUED", "PROCESSING", "SUCCESS", "FAILED", "CANCELLED"] = Field("QUEUED", description="Job state machine")
    product_id: str = Field(..., description="UUID of selected product")
    variant_id: str = Field(..., description="UUID of selected variant")
    input_room_image_url: str = Field(..., description="Uploaded room image")
    analysis_id: Optional[str] = Field(None, description="UUID of RoomAnalysis output")
    result_id: Optional[str] = Field(None, description="UUID of GeneratedResult output")
    error: Optional[str] = Field(None, description="Error reason if job failed")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RoomAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str = Field(...)
    ceiling_polygon: List[List[float]] = Field(default_factory=list, description="List of [x, y] coordinates defining ceiling contour")
    placement_coordinates: Dict[str, float] = Field(default_factory=lambda: {"x": 0.5, "y": 0.25}, description="Computed center (x, y) coordinates [0.0 - 1.0]")
    confidence: float = Field(0.95, ge=0.0, le=1.0, description="Ceiling detection confidence score")
    obstacles: List[Dict[str, Any]] = Field(default_factory=list, description="Detected chandeliers, downlights, beams")
    safe_placement: bool = Field(True, description="Whether position satisfies clearance and safety rules")
    area_ratio: float = Field(0.12, description="Calculated fan-to-ceiling surface area ratio")
    step_status: Dict[str, str] = Field(default_factory=dict, description="Status of individual CV pipeline stages")
    errors: List[str] = Field(default_factory=list, description="Non-fatal warnings or diagnostic messages")


class GeneratedResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Primary UUID of rendered result")
    job_id: str = Field(..., description="UUID of parent generation job")
    image_url: str = Field(..., description="URL of final composed room visualization")
    created_at: Optional[str] = None
