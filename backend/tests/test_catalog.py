"""
Verification Test Suite: User Catalog API.
"""
from fastapi import HTTPException

from backend.app.db.mongo import db_manager
from backend.app.db.seed import seed_database
from backend.app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
)
from backend.app.models.product import FanProductCreate
from backend.app.models.specifications import FanSpecifications
from backend.app.api.routes.admin.products import create_product
from backend.app.api.routes.users.catalog import (
    get_products,
    get_product_details,
    get_active_finishes,
    get_product_variants,
    resolve_variant_combination,
    ResolveVariantRequest,
)


def run_catalog_verification():
    print("==================================================")
    print("Running User Catalog API Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    motor_finishes = finishes_repo.find_all(finish_type="motor", is_active=True)
    blade_finishes = finishes_repo.find_all(finish_type="blade", is_active=True)
    assert len(motor_finishes) > 0 and len(blade_finishes) > 0

    # 1. Get products list
    catalog_products = get_products()
    assert len(catalog_products) > 0
    sample_prod = catalog_products[0]
    print(f"✅ Gate 1: Public catalog retrieved {len(catalog_products)} fans.")

    # 2. Get product details
    details = get_product_details(sample_prod.product_id)
    assert details.product["product_id"] == sample_prod.product_id
    print("✅ Gate 2: Full product details retrieved.")

    # 3. Get active finishes
    finishes = get_active_finishes()
    assert len(finishes) > 0
    print(f"✅ Gate 3: Active finishes retrieved ({len(finishes)} items).")

    # 4. Resolve variant combination
    test_motor = details.motor_finishes[0]["finish_id"] if details.motor_finishes else motor_finishes[0]["finish_id"]
    test_blade = details.blade_finishes[0]["finish_id"] if details.blade_finishes else blade_finishes[0]["finish_id"]
    res = resolve_variant_combination(sample_prod.product_id, ResolveVariantRequest(
        motor_finish_id=test_motor,
        blade_finish_id=test_blade,
    ))
    assert res.is_valid is True
    print("✅ Gate 4: Resolve variant combination verified.")

    print("==================================================")
    print("🎉 ALL USER CATALOG API GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_catalog_verification()
