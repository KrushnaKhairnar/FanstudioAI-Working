"""
Admin Media and AI Asset Management Router.
Manages hero images, variant transparent cutouts, alpha masks, and AI placement configurations.
"""
import asyncio
import uuid
import base64
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.deps import get_db
from app.repositories import (
    ProductsRepository,
    VariantsRepository,
    MediaRepository,
    AiConfigRepository,
    AuditLogsRepository,
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
async def list_product_media(
    product_id: str,
    variant_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all media assets associated with a fan product or specific variant."""
    products_repo = ProductsRepository(db)
    media_repo = MediaRepository(db)

    product = await products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    vid = variant_id if isinstance(variant_id, str) and variant_id else None
    media_items = await media_repo.find_by_product(product_id, variant_id=vid)
    return [ProductMedia(**m) for m in media_items]


@router.post("/products/{product_id}/media", response_model=ProductMedia, status_code=status.HTTP_201_CREATED)
async def create_media(
    product_id: str,
    payload: ProductMediaCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Register a new media file."""
    products_repo = ProductsRepository(db)
    variants_repo = VariantsRepository(db)
    media_repo = MediaRepository(db)
    audit_repo = AuditLogsRepository(db)

    product = await products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    if payload.variant_id:
        variant = await variants_repo.find_by_id(payload.variant_id)
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
        existing_media = await media_repo.find_by_product(product_id, variant_id=payload.variant_id)
        for m in existing_media:
            if m.get("is_primary"):
                await media_repo.update(m["media_id"], {"is_primary": False})

    created = await media_repo.insert(doc)

    media_url = payload.file_url or payload.url
    if payload.variant_id:
        if payload.media_type == "transparent_cutout":
            await variants_repo.update(payload.variant_id, {"transparent_image_url": media_url})
        elif payload.media_type == "variant_render":
            await variants_repo.update(payload.variant_id, {"product_image_url": media_url})

    await audit_repo.log(
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
async def update_media(
    media_id: str,
    payload: ProductMediaUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update media metadata, sort ordering, primary flag, or active status."""
    media_repo = MediaRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing = await media_repo.find_by_id(media_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with ID '{media_id}' not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = await media_repo.update(media_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update media.")

    await audit_repo.log(
        action="UPDATE_MEDIA",
        target_entity="product_media",
        target_id=media_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return ProductMedia(**updated)


@router.delete("/media/{media_id}")
async def delete_media(media_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Delete/deactivate a media asset."""
    media_repo = MediaRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing = await media_repo.find_by_id(media_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with ID '{media_id}' not found.",
        )

    await media_repo.delete(media_id)

    await audit_repo.log(
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
async def get_product_ai_config(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get the AI placement and compositing configuration for a product."""
    products_repo = ProductsRepository(db)
    ai_config_repo = AiConfigRepository(db)

    product = await products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    config = await ai_config_repo.find_by_target("product", product_id)
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
async def update_product_ai_config(
    product_id: str,
    payload: AIProductConfiguration,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update or save the AI placement configuration for a product."""
    products_repo = ProductsRepository(db)
    ai_config_repo = AiConfigRepository(db)
    audit_repo = AuditLogsRepository(db)

    product = await products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    config_data = payload.model_dump()
    config_data["product_id"] = product_id
    saved = await ai_config_repo.upsert_config("product", product_id, config_data)

    await audit_repo.log(
        action="UPDATE_AI_CONFIG",
        target_entity="product",
        target_id=product_id,
        details={"scale": payload.default_scale, "offset": payload.vertical_offset_ratio},
    )

    return AIProductConfiguration(**saved)


@router.get("/variants/{variant_id}/ai-config", response_model=AIProductConfiguration)
async def get_variant_ai_config(variant_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get AI placement configuration specific to a variant."""
    variants_repo = VariantsRepository(db)
    ai_config_repo = AiConfigRepository(db)

    variant = await variants_repo.find_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    config = await ai_config_repo.find_by_target("variant", variant_id)
    if not config:
        parent_config = await ai_config_repo.find_by_target("product", variant["product_id"])
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
async def update_variant_ai_config(
    variant_id: str,
    payload: AIProductConfiguration,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update or save the AI placement configuration for a variant."""
    variants_repo = VariantsRepository(db)
    ai_config_repo = AiConfigRepository(db)
    audit_repo = AuditLogsRepository(db)

    variant = await variants_repo.find_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    config_data = payload.model_dump()
    config_data["product_id"] = variant["product_id"]
    config_data["variant_id"] = variant_id
    saved = await ai_config_repo.upsert_config("variant", variant_id, config_data)

    await audit_repo.log(
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


def _write_upload_file(dest_path: Path, file_bytes: bytes) -> None:
    with open(dest_path, "wb") as f:
        f.write(file_bytes)


@router.post("/media/upload")
async def upload_product_media(
    payload: MediaUploadDirectPayload,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Directly upload a fan image either via base64 data-URL or remote URL."""
    products_repo = ProductsRepository(db)

    await asyncio.to_thread(UPLOADS_DIR.mkdir, parents=True, exist_ok=True)

    product = None
    product_code = "misc"
    if payload.product_id:
        product = await products_repo.find_by_id(payload.product_id) or await products_repo.find_by_code(payload.product_id)
        if product:
            product_code = product.get("product_code") or product.get("fanCode") or payload.product_id

    target_dir = UPLOADS_DIR / "fans" / product_code
    await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)

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
            await asyncio.to_thread(_write_upload_file, dest_path, file_bytes)
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
        await products_repo.update(product["product_id"], update_doc)

    return {
        "success": True,
        "url": saved_rel_path,
        "filename": safe_fname,
        "product_id": payload.product_id,
        "message": "Media uploaded and assigned successfully.",
    }
