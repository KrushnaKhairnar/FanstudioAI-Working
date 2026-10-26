"""
Database Seeding Script for FanStudioAI.
Seeds reusable finishes and baseline catalog data conforming to the platform requirements.
"""
import uuid
import logging
from backend.app.db.mongo import db_manager
from backend.app.repositories import (
    products_repo,
    finishes_repo,
)

logger = logging.getLogger("fanstudioai.seed")


def seed_database():
    """Seeds reusable finishes and initial catalog if database is empty."""
    db_manager.connect()

    # 1. Seed Reusable Finishes
    if finishes_repo.count() == 0:
        motor_finishes = [
            {"name": "Matte Black", "color_code": "#1A1A1A", "sort_order": 1},
            {"name": "Brushed Nickel", "color_code": "#A0A0A0", "sort_order": 2},
            {"name": "Satin Brass", "color_code": "#D4AF37", "sort_order": 3},
            {"name": "Pure Matte White", "color_code": "#F8F9FA", "sort_order": 4},
        ]
        blade_finishes = [
            {"name": "Natural White Oak", "color_code": "#C8AD7F", "sort_order": 1},
            {"name": "Dark Walnut", "color_code": "#3D2B1F", "sort_order": 2},
            {"name": "Matte Black Wood", "color_code": "#212121", "sort_order": 3},
            {"name": "Weathered Ash", "color_code": "#8A8D8F", "sort_order": 4},
        ]

        for item in motor_finishes:
            fid = str(uuid.uuid4())
            doc = {
                "finish_id": fid,
                "name": item["name"],
                "type": "motor",
                "color_code": item["color_code"],
                "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=150&q=80",
                "is_active": True,
                "sort_order": item["sort_order"],
            }
            finishes_repo.insert(doc)

        for item in blade_finishes:
            fid = str(uuid.uuid4())
            doc = {
                "finish_id": fid,
                "name": item["name"],
                "type": "blade",
                "color_code": item["color_code"],
                "image_url": "https://images.unsplash.com/photo-1546484396-fb3fc6f95f98?auto=format&fit=crop&w=150&q=80",
                "is_active": True,
                "sort_order": item["sort_order"],
            }
            finishes_repo.insert(doc)

        logger.info("Seeded reusable motor and blade finishes.")

    # 2. Seed Full Real Fan Catalog (167 real models with motor/blade color combinations)
    prod_count = products_repo.count()
    if prod_count < 10:
        logger.info(f"Products collection has {prod_count} products. Seeding full 167 real fan models...")
        db_manager.seed_database(force=True)
        logger.info(f"Seeding completed. Total products now in database: {products_repo.count()}")
    else:
        logger.info(f"Database already populated with {prod_count} fan products.")


if __name__ == "__main__":
    seed_database()
    print("Database seeding completed successfully.")
