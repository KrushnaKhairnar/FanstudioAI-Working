"""
Database seeding — default finishes upsert (catalog load is scripts/load_data.py).
"""
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import DEFAULT_FINISHES
from app.repositories.finish import FinishesRepository

logger = logging.getLogger("fanstudioai.seed")


async def seed_default_finishes(db: AsyncIOMotorDatabase) -> int:
    """Upsert DEFAULT_FINISHES by finish_id / _id."""
    repo = FinishesRepository(db)
    for f in DEFAULT_FINISHES:
        await repo.upsert_by_id(dict(f))
    logger.info("Upserted %s default finishes", len(DEFAULT_FINISHES))
    return len(DEFAULT_FINISHES)


async def seed_database(db: AsyncIOMotorDatabase) -> None:
    await seed_default_finishes(db)
