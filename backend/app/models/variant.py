"""
FanVariant Domain Model representing an explicit valid motor + blade combination.
Adheres to Master Development Plan Section 5, 6, and 9:
"Finishes define available options. Variants define actual valid combinations."
"Never assume motor_count x blade_count equals actual variants."
"""
import uuid
from typing import Optional
from pydantic import BaseModel, Field


class FanVariantBase(BaseModel):
    product_id: Optional[str] = Field(None, description="UUID of the parent fan product")
    motor_finish_id: str = Field(..., description="UUID of the associated motor finish")
    blade_finish_id: str = Field(..., description="UUID of the associated blade finish")
    sku: Optional[str] = Field(None, max_length=100, description="Optional inventory SKU")
    price_adjustment: float = Field(0.0, description="Optional price differential for this variant")
    product_image_url: Optional[str] = Field(None, description="Primary product rendering of this exact variant")
    transparent_image_url: Optional[str] = Field(None, description="Transparent PNG used for AI room visualization")
    is_active: bool = Field(True, description="Whether this variant is active and selectable by public users")


class FanVariantCreate(FanVariantBase):
    pass


class FanVariantUpdate(BaseModel):
    sku: Optional[str] = None
    price_adjustment: Optional[float] = None
    product_image_url: Optional[str] = None
    transparent_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class FanVariant(FanVariantBase):
    variant_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique UUID identifier for this variant")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "variant_id": "7f8582f3-18ef-4cfa-8186-b4d2427a192d",
                "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "motor_finish_id": "b3f021c3-568e-4a6c-9c59-fb344d5162a8",
                "blade_finish_id": "c4d132d4-679f-5b7d-0d60-fc455e6273b9",
                "sku": "AG52-BLK-OAK",
                "product_image_url": "https://example.com/ag52-black-oak.png",
                "transparent_image_url": "https://example.com/ag52-black-oak-trans.png",
                "is_active": True,
            }
        }
    }
