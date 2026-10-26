"""
Verification Test Suite: Media & AI Asset Management.
"""
from fastapi import HTTPException

from app.db.mongo import db_manager
from app.db.seed import seed_database
from app.repositories import (
    products_repo,
    variants_repo,
    media_repo,
    ai_config_repo,
    audit_repo,
)
from app.models.media import ProductMediaCreate, ProductMediaUpdate
from app.models.ai import AIProductConfiguration
from app.api.routes.admin.media import (
    create_media,
    list_product_media,
    update_media,
    delete_media,
    get_product_ai_config,
    update_product_ai_config,
)


def run_media_verification():
    print("==================================================")
    print("Running Media & AI Asset Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    products = products_repo.find_active()
    assert len(products) > 0, "Active products required"
    prod = products[0]
    product_id = prod["product_id"]

    # 1. Register media
    media_payload = ProductMediaCreate(
        media_type="hero",
        file_url="https://example.com/fans/test_hero.jpg",
        is_primary=True,
        sort_order=1,
    )
    media = create_media(product_id, media_payload)
    assert media.media_id is not None
    assert media.product_id == product_id
    print("✅ Gate 1: Registered media asset.")

    # 2. List media
    media_list = list_product_media(product_id)
    assert len(media_list) > 0
    print(f"✅ Gate 2: Listed {len(media_list)} media items.")

    # 3. AI placement configuration
    ai_config = get_product_ai_config(product_id)
    assert ai_config.default_scale is not None
    print("✅ Gate 3: Product AI configuration retrieved.")

    # 4. Update AI configuration
    saved_config = update_product_ai_config(product_id, AIProductConfiguration(
        product_id=product_id,
        default_scale=1.15,
        vertical_offset_ratio=-0.08,
        lighting_adaptation=True,
    ))
    assert saved_config.default_scale == 1.15
    print("✅ Gate 4: Product AI configuration updated.")

    # 5. Delete media
    del_res = delete_media(media.media_id)
    assert "deleted" in del_res["message"].lower()
    print("✅ Gate 5: Media deletion verified.")

    print("==================================================")
    print("🎉 ALL MEDIA & AI ASSET GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_media_verification()
