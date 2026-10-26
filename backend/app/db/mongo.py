"""
FanStudioAI - MongoDB (Motor async) — sole MongoDB module.
"""
import logging
from typing import Optional
from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

logger = logging.getLogger("fanstudioai.mongo")

DEFAULT_FINISHES = [
    {"finish_id": "mf-matt-grey", "name": "Matt Grey", "type": "motor", "color_code": "#808080", "sort_order": 1, "is_active": True},
    {"finish_id": "mf-matt-black", "name": "Matt Black", "type": "motor", "color_code": "#1A1A1A", "sort_order": 2, "is_active": True},
    {"finish_id": "mf-matt-white", "name": "Matt White", "type": "motor", "color_code": "#F3F4F6", "sort_order": 3, "is_active": True},
    {"finish_id": "mf-antique-bronze", "name": "Antique Bronze", "type": "motor", "color_code": "#8B7355", "sort_order": 4, "is_active": True},
    {"finish_id": "mf-champagne-gold", "name": "Champagne Gold", "type": "motor", "color_code": "#D4AF37", "sort_order": 5, "is_active": True},
    {"finish_id": "mf-walnut", "name": "Walnut", "type": "motor", "color_code": "#5C4033", "sort_order": 6, "is_active": True},
    {"finish_id": "mf-teak", "name": "Teak", "type": "motor", "color_code": "#B3672B", "sort_order": 7, "is_active": True},
    {"finish_id": "bf-teak", "name": "Teak Wooden", "type": "blade", "color_code": "#C27E38", "sort_order": 1, "is_active": True},
    {"finish_id": "bf-rosewood", "name": "Rosewood Wooden", "type": "blade", "color_code": "#5F311C", "sort_order": 2, "is_active": True},
    {"finish_id": "bf-walnut", "name": "Walnut Wooden", "type": "blade", "color_code": "#996933", "sort_order": 3, "is_active": True},
    {"finish_id": "bf-natural-wood", "name": "Natural Wood", "type": "blade", "color_code": "#BA9962", "sort_order": 4, "is_active": True},
    {"finish_id": "bf-cane", "name": "Cane Weave", "type": "blade", "color_code": "#D2A66C", "sort_order": 5, "is_active": True},
    {"finish_id": "bf-matt-black", "name": "Matt Black", "type": "blade", "color_code": "#1A1A1A", "sort_order": 6, "is_active": True},
    {"finish_id": "bf-matt-white", "name": "Matt White", "type": "blade", "color_code": "#F3F4F6", "sort_order": 7, "is_active": True},
    {"finish_id": "bf-oriental-ash", "name": "Oriental Ash", "type": "blade", "color_code": "#D7B88C", "sort_order": 8, "is_active": True},
]

DEFAULT_MOTOR_COLORS = [
    "Matt Grey", "Metallic Grey", "Matt Black", "Matt White",
    "Antique Bronze", "Champagne Gold", "Walnut", "Teak",
]

DEFAULT_BLADE_COLORS = [
    "Teak Wooden", "Rosewood Wooden", "Walnut Wooden",
    "Natural Wood", "Cane Weave", "Matt Black", "Matt White",
]

_client: Optional[AsyncIOMotorClient] = None

COLLECTION_NAMES = [
    "products",
    "finishes",
    "product_variants",
    "product_media",
    "ai_jobs",
    "ai_configurations",
    "rooms",
    "visualization_results",
    "audit_logs",
    "combinations",
    "visualizations",
]


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000,
        )
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGODB_DB_NAME]


def mongo_host_for_log() -> str:
    try:
        parsed = urlparse(settings.MONGODB_URI)
        return parsed.hostname or "localhost"
    except Exception:
        return "localhost"


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    string_exists = {"$type": "string"}
    await db.products.create_index(
        [("product_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"product_id": string_exists},
        name="uniq_product_id",
    )
    await db.products.create_index(
        [("product_code", ASCENDING)],
        unique=True,
        partialFilterExpression={"product_code": string_exists},
        name="uniq_product_code",
    )
    await db.products.create_index([("category", ASCENDING)])
    await db.products.create_index([("status", ASCENDING)])

    await db.finishes.create_index(
        [("finish_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"finish_id": string_exists},
        name="uniq_finish_id",
    )
    await db.finishes.create_index([("type", ASCENDING), ("is_active", ASCENDING)])

    await db.product_variants.create_index(
        [("variant_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"variant_id": string_exists},
        name="uniq_variant_id",
    )
    await db.product_media.create_index(
        [("media_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"media_id": string_exists},
        name="uniq_media_id",
    )
    await db.ai_jobs.create_index(
        [("job_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"job_id": string_exists},
        name="uniq_job_id",
    )
    await db.combinations.create_index(
        [("fan_code", ASCENDING), ("motor_color", ASCENDING), ("blade_color", ASCENDING)],
        unique=True,
        name="uniq_combination_fan_motor_blade",
    )


async def ping_db() -> None:
    client = get_client()
    await client.admin.command("ping")


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def collection_counts(db: AsyncIOMotorDatabase) -> dict:
    counts = {}
    for name in COLLECTION_NAMES:
        try:
            counts[name] = await db[name].count_documents({})
        except Exception:
            counts[name] = 0
    return counts
