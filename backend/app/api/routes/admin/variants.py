"""
Admin Variant Management Router.
Manages explicit valid motor + blade combinations.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
    audit_repo,
)
from app.models.variant import (
    FanVariant,
    FanVariantCreate,
    FanVariantUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Variants"])


class VariantStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Target active status for variant")


class BatchVariantItem(BaseModel):
    motor_finish_id: str
    blade_finish_id: str
    sku: Optional[str] = None
    price_adjustment: float = 0.0
    is_active: bool = True


class BatchVariantRequest(BaseModel):
    combinations: List[BatchVariantItem]


def _validate_combination(product: Dict[str, Any], motor_finish_id: str, blade_finish_id: str):
    """Enforces that finishes are explicitly allowed for this product."""
    allowed_motors = product.get("motor_finish_ids", [])
    allowed_blades = product.get("blade_finish_ids", [])

    if motor_finish_id not in allowed_motors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Motor finish '{motor_finish_id}' is not an approved finish for product '{product.get('name')}'.",
        )

    if blade_finish_id not in allowed_blades:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blade finish '{blade_finish_id}' is not an approved finish for product '{product.get('name')}'.",
        )

    motor_finish = finishes_repo.find_by_id(motor_finish_id)
    blade_finish = finishes_repo.find_by_id(blade_finish_id)
    if not motor_finish or not motor_finish.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Motor finish '{motor_finish_id}' does not exist or is inactive.",
        )
    if not blade_finish or not blade_finish.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blade finish '{blade_finish_id}' does not exist or is inactive.",
        )


@router.get("/products/{product_id}/variants", response_model=List[FanVariant])
def list_product_variants(
    product_id: str,
    only_active: bool = Query(False),
):
    """List all explicit variants registered for a specific product."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    variants = variants_repo.find_by_product(product_id, only_active=only_active)
    return [FanVariant(**v) for v in variants]


@router.get("/variants/{variant_id}", response_model=FanVariant)
def get_variant(variant_id: str):
    """Retrieve a single variant by UUID."""
    variant = variants_repo.find_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )
    return FanVariant(**variant)


@router.post("/products/{product_id}/variants", response_model=FanVariant, status_code=status.HTTP_201_CREATED)
def create_variant(product_id: str, payload: FanVariantCreate):
    """Create a single explicit valid variant combination."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    _validate_combination(product, payload.motor_finish_id, payload.blade_finish_id)

    existing_combination = variants_repo.find_exact(product_id, payload.motor_finish_id, payload.blade_finish_id)
    if existing_combination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This exact motor and blade finish combination is already registered as a variant.",
        )

    sku = payload.sku or f"{product.get('product_code', 'FAN')}-{uuid.uuid4().hex[:6].upper()}"
    existing_sku = variants_repo.find_by_sku(sku)
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SKU '{sku}' is already in use by another variant.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    new_id = str(uuid.uuid4())
    doc = payload.model_dump()
    doc["variant_id"] = new_id
    doc["product_id"] = product_id
    doc["sku"] = sku
    doc["created_at"] = now_iso
    doc["updated_at"] = now_iso

    created = variants_repo.insert(doc)

    audit_repo.log(
        action="CREATE_VARIANT",
        target_entity="variant",
        target_id=new_id,
        details={"product_id": product_id, "sku": sku},
    )

    return FanVariant(**created)


@router.post("/products/{product_id}/variants/batch", response_model=List[FanVariant], status_code=status.HTTP_201_CREATED)
def batch_create_variants(product_id: str, payload: BatchVariantRequest):
    """Batch-register selected matrix variant combinations."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    created_variants: List[FanVariant] = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for item in payload.combinations:
        _validate_combination(product, item.motor_finish_id, item.blade_finish_id)

        existing = variants_repo.find_exact(product_id, item.motor_finish_id, item.blade_finish_id)
        if existing:
            continue

        sku = item.sku or f"{product.get('product_code', 'FAN')}-{uuid.uuid4().hex[:6].upper()}"
        new_id = str(uuid.uuid4())
        doc = {
            "variant_id": new_id,
            "product_id": product_id,
            "motor_finish_id": item.motor_finish_id,
            "blade_finish_id": item.blade_finish_id,
            "sku": sku,
            "price_adjustment": item.price_adjustment,
            "is_active": item.is_active,
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        created = variants_repo.insert(doc)
        created_variants.append(FanVariant(**created))

    audit_repo.log(
        action="BATCH_CREATE_VARIANTS",
        target_entity="product",
        target_id=product_id,
        details={"created_count": len(created_variants)},
    )

    return created_variants


@router.put("/variants/{variant_id}", response_model=FanVariant)
def update_variant(variant_id: str, payload: FanVariantUpdate):
    """Update variant details such as SKU, price adjustment, or active status."""
    existing = variants_repo.find_by_id(variant_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    if payload.sku and payload.sku != existing.get("sku"):
        sku_check = variants_repo.find_by_sku(payload.sku)
        if sku_check and sku_check.get("variant_id") != variant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU '{payload.sku}' is already in use by another variant.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = variants_repo.update(variant_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update variant.")

    audit_repo.log(
        action="UPDATE_VARIANT",
        target_entity="variant",
        target_id=variant_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return FanVariant(**updated)


@router.patch("/variants/{variant_id}/status", response_model=FanVariant)
def update_variant_status(variant_id: str, payload: VariantStatusUpdate):
    """Toggle variant active/inactive status."""
    existing = variants_repo.find_by_id(variant_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    updated = variants_repo.set_active(variant_id, payload.is_active)

    audit_repo.log(
        action="UPDATE_VARIANT_STATUS",
        target_entity="variant",
        target_id=variant_id,
        details={"is_active": payload.is_active},
    )

    return FanVariant(**updated)


@router.delete("/variants/{variant_id}")
def deactivate_variant(variant_id: str):
    """Soft-deactivate variant (sets is_active to false)."""
    existing = variants_repo.find_by_id(variant_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID '{variant_id}' not found.",
        )

    variants_repo.set_active(variant_id, False)

    audit_repo.log(
        action="DEACTIVATE_VARIANT",
        target_entity="variant",
        target_id=variant_id,
        details={"sku": existing.get("sku")},
    )

    return {
        "message": f"Variant '{existing.get('sku')}' successfully deactivated.",
        "variant_id": variant_id,
        "is_active": False,
    }
