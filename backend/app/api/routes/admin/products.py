"""
Admin Product Management Router.
Full CRUD, specifications, deactivation lifecycle, and bulk import.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.deps import get_db
from app.repositories import (
    ProductsRepository,
    FinishesRepository,
    AuditLogsRepository,
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
async def list_products(
    status_filter: Optional[Literal["draft", "active", "inactive"]] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 500,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all products in catalog with optional status filtering."""
    products_repo = ProductsRepository(db)
    if status_filter:
        products = await products_repo.find_by_status(status_filter, skip=skip, limit=limit)
    else:
        products = await products_repo.find_all(skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Retrieve a single fan product by its unique product_id UUID."""
    products_repo = ProductsRepository(db)
    product = await products_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return product


@router.post("", response_model=FanProduct, status_code=status.HTTP_201_CREATED)
async def create_product(payload: FanProductCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new fan product in the catalog."""
    products_repo = ProductsRepository(db)
    finishes_repo = FinishesRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing_code = await products_repo.find_by_code(payload.product_code)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product code '{payload.product_code}' is already registered.",
        )

    for mid in payload.motor_finish_ids:
        if not await finishes_repo.find_by_id(mid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Motor finish ID '{mid}' does not exist.",
            )

    for bid in payload.blade_finish_ids:
        if not await finishes_repo.find_by_id(bid):
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

    created = await products_repo.insert(doc)

    await audit_repo.log(
        action="CREATE_PRODUCT",
        target_entity="product",
        target_id=new_id,
        details={"product_code": payload.product_code, "name": payload.name},
    )

    return FanProduct(**created)


@router.put("/{product_id}", response_model=FanProduct)
async def update_product(
    product_id: str,
    payload: FanProductUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update existing fan product specification, status, or finish relationships."""
    products_repo = ProductsRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing = await products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    if payload.product_code and payload.product_code != existing.get("product_code"):
        duplicate = await products_repo.find_by_code(payload.product_code)
        if duplicate and duplicate.get("product_id") != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product code '{payload.product_code}' is in use by another product.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    updated = await products_repo.update(product_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist product update.",
        )

    await audit_repo.log(
        action="UPDATE_PRODUCT",
        target_entity="product",
        target_id=product_id,
        details={"updated_fields": list(update_data.keys())},
    )

    return FanProduct(**updated)


@router.patch("/{product_id}/status", response_model=FanProduct)
async def update_product_status(
    product_id: str,
    payload: ProductStatusUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Transition product status between draft, active, and inactive."""
    products_repo = ProductsRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing = await products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    updated = await products_repo.update(product_id, {
        "status": payload.status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    await audit_repo.log(
        action="UPDATE_PRODUCT_STATUS",
        target_entity="product",
        target_id=product_id,
        details={"previous_status": existing.get("status"), "new_status": payload.status},
    )

    return FanProduct(**updated)


@router.delete("/{product_id}")
async def deactivate_product(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Soft-deactivate product (sets status to inactive). Never hard-deletes active products."""
    products_repo = ProductsRepository(db)
    audit_repo = AuditLogsRepository(db)

    existing = await products_repo.find_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    await products_repo.soft_delete_or_deactivate(product_id)

    await audit_repo.log(
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
async def batch_import_products(payload: Any, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Bulk import products into the catalog."""
    products_repo = ProductsRepository(db)
    audit_repo = AuditLogsRepository(db)

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

        existing = await products_repo.find_by_id(p_id) or await products_repo.find_by_code(fan_code)
        if existing:
            await products_repo.update(existing["product_id"], doc)
        else:
            await products_repo.insert(doc)
        imported_count += 1

    await audit_repo.log(
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
