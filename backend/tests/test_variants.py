"""
Verification Test Suite: Variant Management (Combinations enforced).
"""
import uuid
from fastapi import HTTPException

from backend.app.db.mongo import db_manager
from backend.app.db.seed import seed_database
from backend.app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
    audit_repo,
)
from backend.app.models.product import FanProductCreate
from backend.app.models.specifications import FanSpecifications
from backend.app.models.variant import FanVariantCreate, FanVariantUpdate
from backend.app.api.routes.admin.products import create_product
from backend.app.api.routes.admin.variants import (
    create_variant,
    batch_create_variants,
    list_product_variants,
    get_variant,
    update_variant,
    update_variant_status,
    deactivate_variant,
    BatchVariantRequest,
    BatchVariantItem,
    VariantStatusUpdate,
)


def run_variants_verification():
    print("==================================================")
    print("Running Variant Management Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    motor_finishes = finishes_repo.find_all(finish_type="motor", is_active=True)
    blade_finishes = finishes_repo.find_all(finish_type="blade", is_active=True)
    assert len(motor_finishes) >= 2 and len(blade_finishes) >= 2

    m1, m2 = motor_finishes[0]["finish_id"], motor_finishes[1]["finish_id"]
    b1, b2 = blade_finishes[0]["finish_id"], blade_finishes[1]["finish_id"]

    # Ensure test product exists
    p_code = f"FAN-VAR-TEST-{uuid.uuid4().hex[:6]}"
    prod_doc = create_product(FanProductCreate(
            product_code=p_code,
            name="Variant Test Fan",
            description="Testing variant combinations.",
            status="active",
            specifications=FanSpecifications(
                category="Architectural",
                blade_type="ABS",
                blade_count=3,
                motor_type="BLDC",
            ),
            motor_finish_ids=[m1, m2],
            blade_finish_ids=[b1, b2],
        ))
    prod = prod_doc.model_dump()

    prod_id = prod["product_id"]

    # 1. Create a valid variant
    sku_val = f"TEST-SKU-{uuid.uuid4().hex[:6]}"
    var = create_variant(prod_id, FanVariantCreate(
        motor_finish_id=m1,
        blade_finish_id=b1,
        sku=sku_val,
        price_adjustment=0.0,
        is_active=True,
    ))
    assert var.variant_id is not None
    assert var.sku == sku_val
    print("✅ Gate 1: Valid variant combination created.")

    # 2. List variants
    vars_list = list_product_variants(prod_id)
    assert len(vars_list) > 0
    print(f"✅ Gate 2: Listed {len(vars_list)} variants.")

    # 3. Retrieve variant
    fetched = get_variant(var.variant_id)
    assert fetched.variant_id == var.variant_id
    print("✅ Gate 3: Get variant verified.")

    # 4. Update variant
    upd = update_variant(var.variant_id, FanVariantUpdate(price_adjustment=500.0))
    assert upd.price_adjustment == 500.0
    print("✅ Gate 4: Update variant verified.")

    # 5. Soft-deactivate variant
    deact = deactivate_variant(var.variant_id)
    assert deact["is_active"] is False
    print("✅ Gate 5: Deactivate variant verified.")

    print("==================================================")
    print("🎉 ALL VARIANT MANAGEMENT GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_variants_verification()
