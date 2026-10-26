"""
Admin Media and AI Asset Management Router.
Manages hero images, variant transparent cutouts, alpha masks, and AI placement configurations.
"""
import os
import uuid
import base64
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.repositories import (
    products_repo,
    variants_repo,
    media_repo,
    ai_config_repo,
    audit_repo,
)
from app.models.media import (
    ProductMedia,
    ProductMediaCreate,
    ProductMediaUpdate,
)
from app.models.ai import (
    AIProductConfiguration,
)
from app.core.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin Media & AI Assets"])

UPLOADS_DIR = Path(settings.UPLOAD_DIR)


@router.get("/products/{product_id}/media", response_model=List[ProductMedia])
def list_product_media(
    product_id: str,
    variant_id: Optional[str] = Query(None),
):
    """List all media assets associated with a fan product or specific variant."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    vid = variant_id if isinstance(variant_id, str) and variant_id else None
    media_items = media_repo.find_by_product(product_id, variant_id=vid)
    return [ProductMedia(**m) for m in media_items]


@router.post("/products/{product_id}/media", response_model=ProductMedia, status_code=status.HTTP_201_CREATED)
def create_media(
    product_id: str,
    payload: ProductMediaCreate,
):
    """Register a new media file."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    if payload.variant_id:
        variant = variants_repo.find_by_id(payload.variant_id)
        if not variant or variant.get("product_id") != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Variant '{payload.variant_id}' does not belong to product '{product_id}'.",
            )

    now_iso = datetime.now(timezone.utc).isoformat()
    new_id = str(uuid.uuid4())
    doc = payload.model_dump()
    doc["media_id"] = new_id
    doc["product_id"] = product_id
    doc["created_at"] = now_iso
    doc["updated_at"] = now_iso

    if payload.is_primary:
        existing_media = media_repo.find_by_product(product_id, variant_id=payload.variant_id)
        for m in existing_media:
            if m.get("is_primary"):
                media_repo.update(m["media_id"], {"is_primary": False})

    created = media_repo.insert(doc)

    media_url = payload.file_url or payload.url
    if payload.variant_id:
        if payload.media_type == "transparent_cutout":
            variants_repo.update(payload.variant_id, {"transparent_image_url": media_url})
        elif payload.media_type == "variant_render":
            variants_repo.update(payload.variant_id, {"product_image_url": media_url})

    audit_repo.log(
        action="CREATE_MEDIA",
        target_entity="product_media",
        target_id=new_id,
        details={
            "product_id": product_id,
            "variant_id": payload.variant_id,
            "media_type": payload.media_type,
            "file_url": media_url,
        },
    )

    return ProductMedia(**created)


@router.put("/media/{media_id}", response_model=ProductMedia)
def update_media(
    media_id: str,
    payload: ProductMediaUpdate,
):
    """Update media metadata, sort ordering, primary flag, or active status."""
    existing = media_repo.find_by_id(media_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with ID '{media_id}' not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = media_repo.update(media_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update media.")

    audit_repo.log(
        action="UPDATE_MEDIA",
        target_entity="product_media",
        target_id=media_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return ProductMedia(**updated)


@router.delete("/media/{media_id}")
def delete_media(media_id: str):
    """Delete/deactivate a media asset."""
    existing = media_repo.find_by_id(media_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with ID '{media_id}' not found.",
        )

    media_repo.delete(media_id)

    audit_repo.log(
        action="DELETE_MEDIA",
        target_entity="product_media",
        target_id=media_id,
        details={"file_url": existing.get("file_url")},
    )

    return {
        "message": "Media asset deleted successfully.",
        "media_id": media_id,
    }


@router.get("/products/{product_id}/ai-config", response_model=AIProductConfiguration)
def get_product_ai_config(product_id: str):
    """Get the AI placement and compositing configuration for a product."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    config = ai_config_repo.find_by_target("product", product_id)
    if not config:
        return AIProductConfiguration(
            product_id=product_id,
            default_scale=1.0,
            vertical_offset_ratio=-0.05,
            lighting_adaptation=True,
            blending_mode="perspective_composite",
        )

    return AIProductConfiguration(**config)


@router.put("/products/{product_id}/ai-config", response_model=AIProductConfiguration)
def update_product_ai_config(
    product_id: str,
    payload: AIProductConfiguration,
):
    """Update or save the AI placement configuration for a product."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    config_data = payload.model_dump()
    config_data["product_id"] = product_id
    saved = ai_config_repo.upsert_config("product", product_id, config_data)

    audit_repo.log(
        action="UPDATE_AI_CONFIG",
        target_entity="product",
        target_id=product_id,
        details={"scale": payload.default_scale, "offset": payload.vertical_offset_ratio},
    )

    return AIProductConfiguration(**saved)


@router.get("/variants/{variant_id}/ai-config", response_model=AIProductConfiguration)
def get_variant_ai_config(variant_id: str):
    """Get AI placement configuration specific to a variant."""
    variant = variants_repo.find_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    config = ai_config_repo.find_by_target("variant", variant_id)
    if not config:
        parent_config = ai_config_repo.find_by_target("product", variant["product_id"])
        if parent_config:
            parent_config["variant_id"] = variant_id
            return AIProductConfiguration(**parent_config)

        return AIProductConfiguration(
            product_id=variant["product_id"],
            variant_id=variant_id,
            transparent_png_url=variant.get("transparent_image_url"),
            default_scale=1.0,
            vertical_offset_ratio=-0.05,
            lighting_adaptation=True,
            blending_mode="perspective_composite",
        )

    return AIProductConfiguration(**config)


@router.put("/variants/{variant_id}/ai-config", response_model=AIProductConfiguration)
def update_variant_ai_config(
    variant_id: str,
    payload: AIProductConfiguration,
):
    """Update or save the AI placement configuration for a variant."""
    variant = variants_repo.find_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    config_data = payload.model_dump()
    config_data["product_id"] = variant["product_id"]
    config_data["variant_id"] = variant_id
    saved = ai_config_repo.upsert_config("variant", variant_id, config_data)

    audit_repo.log(
        action="UPDATE_AI_CONFIG",
        target_entity="variant",
        target_id=variant_id,
        details={"scale": payload.default_scale, "offset": payload.vertical_offset_ratio},
    )

    return AIProductConfiguration(**saved)


class MediaUploadDirectPayload(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    filename: Optional[str] = None
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    is_primary: Optional[bool] = True


@router.post("/media/upload")
def upload_product_media(payload: MediaUploadDirectPayload):
    """Directly upload a fan image either via base64 data-URL or remote URL."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    product = None
    product_code = "misc"
    if payload.product_id:
        product = products_repo.find_by_id(payload.product_id) or products_repo.find_by_code(payload.product_id)
        if product:
            product_code = product.get("product_code") or product.get("fanCode") or payload.product_id

    target_dir = UPLOADS_DIR / "fans" / product_code
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_rel_path = None
    fname = payload.filename or f"{product_code}_upload.jpg"
    safe_fname = "".join(c for c in fname if c.isalnum() or c in "._-")
    dest_path = target_dir / safe_fname

    if payload.image_base64:
        b64_data = payload.image_base64
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        try:
            file_bytes = base64.b64decode(b64_data)
            with open(dest_path, "wb") as f:
                f.write(file_bytes)
            saved_rel_path = f"/uploads/fans/{product_code}/{safe_fname}"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode base64 image: {str(e)}")
    elif payload.image_url:
        saved_rel_path = payload.image_url
    else:
        raise HTTPException(status_code=400, detail="Either image_base64 or image_url must be provided.")

    if product and saved_rel_path:
        update_doc = {}
        if payload.is_primary:
            update_doc["primary_image_url"] = saved_rel_path
            update_doc["imagePath"] = saved_rel_path
        existing_images = product.get("images") or []
        if saved_rel_path not in existing_images:
            update_doc["images"] = [saved_rel_path] + [img for img in existing_images if img != saved_rel_path]
        products_repo.update(product["product_id"], update_doc)

    return {
        "success": True,
        "url": saved_rel_path,
        "filename": safe_fname,
        "product_id": payload.product_id,
        "message": "Media uploaded and assigned successfully.",
    }
