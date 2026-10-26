"""
Admin Product Management Router.
Full CRUD, specifications, deactivation lifecycle, and bulk import.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.repositories import (
    products_repo,
    finishes_repo,
    audit_repo,
)
from app.models.product import (
    FanProduct,
    FanProductCreate,
    FanProductUpdate,
)
from app.db.mongo import DEFAULT_MOTOR_COLORS, DEFAULT_BLADE_COLORS

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])


class ProductStatusUpdate(BaseModel):
    status: Literal["draft", "active", "inactive"] = Field(..., description="Target status")


@router.get("", response_model=List[Dict[str, Any]])
def list_products(
    status_filter: Optional[Literal["draft", "active", "inactive"]] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 500,
):
    """List all products in catalog with optional status filtering."""
    if status_filter:
        products = products_repo.find_by_status(status_filter, skip=skip, limit=limit)
    else:
        products = products_repo.find_all(skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=Dict[str, Any])
def get_product(product_id: str):
    """Retrieve a single fan product by its unique product_id UUID."""
    product = products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return product


@router.post("", response_model=FanProduct, status_code=status.HTTP_201_CREATED)
def create_product(payload: FanProductCreate):
    """Create a new fan product in the catalog."""
    existing_code = products_repo.find_by_code(payload.product_code)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product code '{payload.product_code}' is already registered.",
        )

    for mid in payload.motor_finish_ids:
        if not finishes_repo.find_by_id(mid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Motor finish ID '{mid}' does not exist.",
            )

    for bid in payload.blade_finish_ids:
        if not finishes_repo.find_by_id(bid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Blade finish ID '{bid}' does not exist.",
            )

    now_iso = datetime.now(timezone.utc).isoformat()
    new_id = str(uuid.uuid4())
    doc = payload.model_dump()
    doc["product_id"] = new_id
    doc["created_at"] = now_iso
    doc["updated_at"] = now_iso

    created = products_repo.insert(doc)

    audit_repo.log(
        action="CREATE_PRODUCT",
        target_entity="product",
        target_id=new_id,
        details={"product_code": payload.product_code, "name": payload.name},
    )

    return FanProduct(**created)


@router.put("/{product_id}", response_model=FanProduct)
def update_product(product_id: str, payload: FanProductUpdate):
    """Update existing fan product specification, status, or finish relationships."""
    existing = products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    if payload.product_code and payload.product_code != existing.get("product_code"):
        duplicate = products_repo.find_by_code(payload.product_code)
        if duplicate and duplicate.get("product_id") != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product code '{payload.product_code}' is in use by another product.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = products_repo.update(product_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist product update.",
        )

    audit_repo.log(
        action="UPDATE_PRODUCT",
        target_entity="product",
        target_id=product_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return FanProduct(**updated)


@router.patch("/{product_id}/status", response_model=FanProduct)
def update_product_status(product_id: str, payload: ProductStatusUpdate):
    """Transition product status between draft, active, and inactive."""
    existing = products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    updated = products_repo.update(product_id, {
        "status": payload.status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    audit_repo.log(
        action="UPDATE_PRODUCT_STATUS",
        target_entity="product",
        target_id=product_id,
        details={"previous_status": existing.get("status"), "new_status": payload.status},
    )

    return FanProduct(**updated)


@router.delete("/{product_id}")
def deactivate_product(product_id: str):
    """Soft-deactivate product (sets status to inactive). Never hard-deletes active products."""
    existing = products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    products_repo.soft_delete_or_deactivate(product_id)

    audit_repo.log(
        action="DEACTIVATE_PRODUCT",
        target_entity="product",
        target_id=product_id,
        details={"name": existing.get("name"), "product_code": existing.get("product_code")},
    )

    return {
        "message": f"Product '{existing.get('name')}' successfully deactivated.",
        "product_id": product_id,
        "status": "inactive",
    }


@router.post("/batch-import")
def batch_import_products(payload: Any):
    """Bulk import products into the catalog."""
    products_to_import = []
    if isinstance(payload, list):
        products_to_import = payload
    elif isinstance(payload, dict):
        if "products" in payload and isinstance(payload["products"], list):
            products_to_import = payload["products"]
        else:
            products_to_import = [payload]

    imported_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for item in products_to_import:
        if not isinstance(item, dict):
            continue
        p_id = item.get("product_id") or item.get("productId") or str(uuid.uuid4())
        fan_code = item.get("product_code") or item.get("fanCode") or p_id
        name = item.get("name") or item.get("fanName") or "Ceiling Fan"
        
        motor_colors = item.get("motor_colors") or DEFAULT_MOTOR_COLORS
        blade_colors = item.get("blade_colors") or DEFAULT_BLADE_COLORS
        default_motor = item.get("default_motor_color") or motor_colors[0]
        default_blade = item.get("default_blade_color") or blade_colors[0]

        combinations = item.get("color_combinations") or []
        if not combinations:
            for mc in motor_colors:
                m_slug = mc.lower().replace(" ", "-")
                for bc in blade_colors:
                    b_slug = bc.lower().replace(" ", "-")
                    combinations.append({
                        "combination_id": f"comb-{m_slug}-{b_slug}",
                        "motor_color": mc,
                        "blade_color": bc,
                        "image_url": f"/api/users/combination-image?fan_code={fan_code}&motor_color={mc}&blade_color={bc}",
                        "transparent_image_url": f"/api/users/combination-image?fan_code={fan_code}&motor_color={mc}&blade_color={bc}&transparent=true",
                        "price": float(item.get("price") or item.get("base_price") or 14999.0)
                    })

        doc = {
            **item,
            "product_id": p_id,
            "product_code": fan_code,
            "fanCode": fan_code,
            "name": name,
            "fanName": name,
            "status": item.get("status") or "active",
            "motor_colors": motor_colors,
            "blade_colors": blade_colors,
            "default_motor_color": default_motor,
            "default_blade_color": default_blade,
            "color_combinations": combinations,
            "updated_at": now_iso,
        }
        if "created_at" not in doc:
            doc["created_at"] = now_iso

        existing = products_repo.find_by_id(p_id) or products_repo.find_by_code(fan_code)
        if existing:
            products_repo.update(existing["product_id"], doc)
        else:
            products_repo.insert(doc)
        imported_count += 1

    audit_repo.log(
        action="BATCH_IMPORT_PRODUCTS",
        target_entity="product",
        target_id="bulk",
        details={"count": imported_count},
    )

    return {
        "status": "success",
        "count": imported_count,
        "message": f"Successfully imported {imported_count} products",
    }
