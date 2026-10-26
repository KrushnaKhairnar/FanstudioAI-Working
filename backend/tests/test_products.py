"""
Verification Test Suite: Admin Product Management.
"""
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.db.mongo import db_manager
from backend.app.db.seed import seed_database
from backend.app.repositories import products_repo, finishes_repo, audit_repo
from backend.app.models.product import FanProductCreate, FanProductUpdate
from backend.app.models.specifications import FanSpecifications
from backend.app.api.routes.admin.products import (
    create_product,
    list_products,
    get_product,
    update_product,
    update_product_status,
    deactivate_product,
    ProductStatusUpdate,
)


def run_products_verification():
    print("==================================================")
    print("Running Admin Product Management Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    motor_finishes = finishes_repo.find_all(finish_type="motor", is_active=True)
    blade_finishes = finishes_repo.find_all(finish_type="blade", is_active=True)
    assert len(motor_finishes) > 0 and len(blade_finishes) > 0, "Finishes required"

    sample_motor_id = motor_finishes[0]["finish_id"]
    sample_blade_id = blade_finishes[0]["finish_id"]

    old_test_p = products_repo.find_by_code("FAN-VERIFY-01")
    if old_test_p:
        products_repo.collection.delete_one({"product_code": "FAN-VERIFY-01"})

    # 1. Create Product
    valid_payload = FanProductCreate(
        product_code="FAN-VERIFY-01",
        name="AeroBreeze Horizon",
        description="Sculptural architectural ceiling fan with high efficiency DC motor.",
        status="active",
        specifications=FanSpecifications(
            category="Modern Architectural",
            blade_type="Carved Solid Timber",
            blade_count=3,
            motor_type="Precision Brushless DC",
        ),
        motor_finish_ids=[sample_motor_id],
        blade_finish_ids=[sample_blade_id],
    )
    created_prod = create_product(valid_payload)
    assert created_prod.product_id is not None
    assert created_prod.product_code == "FAN-VERIFY-01"
    assert created_prod.status == "active"
    prod_id = created_prod.product_id
    print("✅ Gate 1: Product created with valid specifications.")

    # 2. Enforce Unique Product Code
    try:
        duplicate_payload = FanProductCreate(
            product_code="FAN-VERIFY-01",
            name="Duplicate Code Attempt",
            status="draft",
            specifications=FanSpecifications(
                category="Contemporary",
                blade_type="ABS",
                blade_count=4,
                motor_type="DC",
            ),
            motor_finish_ids=[sample_motor_id],
            blade_finish_ids=[sample_blade_id],
        )
        create_product(duplicate_payload)
        assert False, "Expected 400 error on duplicate product_code"
    except HTTPException as e:
        assert e.status_code == 400
        print("✅ Gate 2: Duplicate product_code blocked.")

    # 3. List Products
    all_products = list_products(status_filter=None)
    assert len(all_products) >= 2, f"Expected at least 2 products, found {len(all_products)}"

    # 4. Get Product by ID
    fetched = get_product(prod_id)
    fetched_id = fetched.product_id if hasattr(fetched, "product_id") else fetched.get("product_id")
    fetched_name = fetched.name if hasattr(fetched, "name") else fetched.get("name")
    assert fetched_id == prod_id
    assert fetched_name == "AeroBreeze Horizon"
    print("✅ Gate 3: Get product by ID verified.")

    # 5. Update Product Details
    update_payload = FanProductUpdate(
        name="AeroBreeze Horizon Elite",
        description="Updated high-end architectural ceiling fan.",
    )
    updated = update_product(prod_id, update_payload)
    assert updated.name == "AeroBreeze Horizon Elite"
    print("✅ Gate 4: Update product details verified.")

    # 6. Soft-deactivation
    deactivate_res = deactivate_product(prod_id)
    assert deactivate_res["status"] == "inactive"
    db_record = products_repo.find_by_id(prod_id)
    assert db_record is not None
    assert db_record["status"] == "inactive"
    print("✅ Gate 5: Soft-deactivation verified.")

    print("==================================================")
    print("🎉 ALL PRODUCT MANAGEMENT GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_products_verification()
