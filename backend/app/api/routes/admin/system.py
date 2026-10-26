"""
Admin System & Operations Router.
Provides database status inspection, catalog reload from disk, and audit logs.
"""
from typing import Dict, Any, List
from fastapi import APIRouter

from app.db.mongo import db_manager
from app.repositories import products_repo, audit_repo

router = APIRouter(prefix="/api/admin", tags=["Admin System"])


@router.get("/mongodb/status")
def get_mongodb_status() -> Dict[str, Any]:
    """Retrieve current MongoDB connection, engine type, and collection counts."""
    return db_manager.get_status()


@router.post("/products/reload")
def reload_products_from_disk() -> Dict[str, Any]:
    """Reloads catalog products and finishes from disk (data/catalog.json) into database."""
    db_manager.seed_database(force=True)
    count = products_repo.count()
    return {
        "success": True,
        "count": count,
        "message": f"Reloaded {count} products from disk into database memory!",
    }


@router.post("/reload")
def reload_catalog_alias() -> Dict[str, Any]:
    """Alias for catalog reload endpoint."""
    return reload_products_from_disk()


@router.get("/audit-logs")
def get_audit_logs() -> List[Dict[str, Any]]:
    """Retrieve recent system audit logs."""
    logs = audit_repo.find_recent(limit=50)
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
