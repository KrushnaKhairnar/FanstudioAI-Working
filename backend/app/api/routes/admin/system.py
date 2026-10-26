"""
Admin System & Operations Router.
Provides database status inspection, catalog reload from disk, and audit logs.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.deps import get_db
from app.db.mongo import collection_counts
from app.db.seed import seed_database
from app.repositories import ProductsRepository, FinishesRepository, VariantsRepository, AuditLogsRepository

router = APIRouter(prefix="/api/admin", tags=["Admin System"])


async def _load_catalog_from_disk(db: AsyncIOMotorDatabase) -> None:
    """Load products, finishes, and variants from data/catalog.json if present."""
    catalog_path = Path(settings.DATA_DIR) / "catalog.json"
    if not catalog_path.is_file():
        return

    def _read_catalog() -> dict:
        return json.loads(catalog_path.read_text(encoding="utf-8"))

    data = await asyncio.to_thread(_read_catalog)
    products_repo = ProductsRepository(db)
    finishes_repo = FinishesRepository(db)
    variants_repo = VariantsRepository(db)

    for f in data.get("finishes", []):
        fd = dict(f)
        if fd.get("finish_id"):
            await finishes_repo.upsert_by_id(fd)

    for p in data.get("products", []):
        doc = dict(p)
        pid = doc.get("product_id") or doc.get("productId")
        if not pid:
            continue
        doc["product_id"] = pid
        existing = await products_repo.find_by_id(pid)
        if existing:
            await products_repo.update(pid, doc)
        else:
            await products_repo.insert(doc)

    for v in data.get("variants", []):
        doc = dict(v)
        vid = doc.get("variant_id")
        if not vid:
            continue
        existing = await variants_repo.find_by_id(vid)
        if existing:
            await variants_repo.update(vid, doc)
        else:
            await variants_repo.insert(doc)


async def _reload_products_from_disk(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    await seed_database(db)
    await _load_catalog_from_disk(db)
    products_repo = ProductsRepository(db)
    count = await products_repo.count()
    return {
        "success": True,
        "count": count,
        "message": f"Reloaded {count} products from disk into database memory!",
    }


@router.get("/mongodb/status")
async def get_mongodb_status(db: AsyncIOMotorDatabase = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve current MongoDB connection, engine type, and collection counts."""
    collections = await collection_counts(db)
    return {
        "database": settings.MONGODB_DB_NAME,
        "collections": collections,
        "is_live": True,
        "engine": "mongodb",
    }


@router.post("/products/reload")
async def reload_products_from_disk(db: AsyncIOMotorDatabase = Depends(get_db)) -> Dict[str, Any]:
    """Reloads catalog products and finishes from disk (data/catalog.json) into database."""
    return await _reload_products_from_disk(db)


@router.post("/reload")
async def reload_catalog_alias(db: AsyncIOMotorDatabase = Depends(get_db)) -> Dict[str, Any]:
    """Alias for catalog reload endpoint."""
    return await _reload_products_from_disk(db)


@router.get("/audit-logs")
async def get_audit_logs(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieve recent system audit logs."""
    audit_repo = AuditLogsRepository(db)
    logs = await audit_repo.find_recent(limit=50)
    formatted = []
    for l in logs:
        l_copy = dict(l)
        if "_id" in l_copy:
            l_copy["_id"] = str(l_copy["_id"])
        l_copy.setdefault("id", l_copy.get("log_id"))
        l_copy.setdefault("timestamp", l_copy.get("created_at"))
        l_copy.setdefault("entity_type", l_copy.get("target_entity"))
        l_copy.setdefault("entity_id", l_copy.get("target_id"))
        formatted.append(l_copy)
    return formatted
