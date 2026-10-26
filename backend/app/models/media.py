"""
ProductMedia Domain Model representing image assets associated with products and variants.
Adheres to Master Development Plan Section 5, 8 & 12.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, Field


class ProductMediaBase(BaseModel):
    product_id: Optional[str] = Field(None, description="UUID of parent fan product")
    variant_id: Optional[str] = Field(None, description="Optional UUID of associated variant")
    url: str = Field("", description="Secure image/asset URL")
    file_url: Optional[str] = Field(None, description="Alternative alias for url")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    media_type: str = Field("hero", description="Media type: hero, gallery, variant_render, transparent_cutout, alpha_mask")
    mime_type: Optional[str] = Field("image/jpeg", description="MIME type of media")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    width: Optional[int] = Field(None, description="Width in pixels")
    height: Optional[int] = Field(None, description="Height in pixels")
    title: Optional[str] = Field(None, max_length=150, description="Media caption or title")
    is_primary: bool = Field(False, description="Whether this is the primary hero image")
    sort_order: int = Field(0, description="Gallery ordering index")
    is_active: bool = Field(True, description="Active status")

    def model_post_init(self, __context):
        if not self.url and self.file_url:
            self.url = self.file_url
        elif not self.file_url and self.url:
            self.file_url = self.url


class ProductMediaCreate(ProductMediaBase):
    pass


class ProductMediaUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    file_url: Optional[str] = None
    is_primary: Optional[bool] = None
    sort_order: Optional[int] = None
    variant_id: Optional[str] = None
    is_active: Optional[bool] = None


class ProductMedia(ProductMediaBase):
    media_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Primary UUID identifier for media asset")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "media_id": "9d8e7f6a-5b4c-3d2e-1f0a-9b8c7d6e5f4a",
                "product_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "variant_id": "7f8582f3-18ef-4cfa-8186-b4d2427a192d",
                "url": "https://storage.googleapis.com/fanstudio-assets/fans/aeroglide/ag52-blk-cutout.png",
                "media_type": "transparent_cutout",
                "title": "AeroGlide Matte Black Cutout",
                "is_primary": False,
                "sort_order": 1,
            }
        }
    }
