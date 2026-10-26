"""
Finish Domain Model for reusable Motor and Blade finishes.
Adheres to Master Development Plan Section 5 & 6.
"""
import uuid
from typing import Optional, Literal
from pydantic import BaseModel, Field


class FinishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the finish")
    type: Literal["motor", "blade"] = Field(..., description="Finish type: motor or blade")
    color_code: Optional[str] = Field(None, max_length=20, description="Hex color or styling code")
    image_url: Optional[str] = Field(None, description="Finish swatch image URL")
    is_active: bool = Field(True, description="Whether the finish is active and available for variants")
    sort_order: int = Field(0, description="Display sort order")


class FinishCreate(FinishBase):
    pass


class FinishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[Literal["motor", "blade"]] = None
    color_code: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class Finish(FinishBase):
    finish_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique UUID identifier for the finish")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "finish_id": "b3f021c3-568e-4a6c-9c59-fb344d5162a8",
                "name": "Matte Black",
                "type": "motor",
                "color_code": "#1A1A1A",
                "image_url": "https://example.com/matte-black.png",
                "is_active": True,
                "sort_order": 1,
            }
        }
    }
