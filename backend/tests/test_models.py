"""
Verification Test Suite: Domain Models Validation.
"""
import uuid
from pydantic import ValidationError

from app.models import (
    FanSpecifications,
    Finish,
    FinishCreate,
    FanVariant,
    FanProduct,
    FanProductCreate,
    AIProductConfiguration,
    AIJob,
)


def run_models_verification():
    print("==================================================")
    print("Running Pydantic Domain Model Verification...")
    print("==================================================")

    # 1. Gate 1: FanSpecifications Validation
    valid_specs = FanSpecifications(
        category="Modern Luxury",
        blade_type="Aerodynamic Composite",
        blade_count=3,
        motor_type="Precision DC Motor",
    )
    assert valid_specs.blade_count == 3
    print("✅ Gate 1: Valid specifications parsed successfully.")

    # 2. Gate 2: Finish Validation
    valid_finish = FinishCreate(
        name="Brushed Champagne Brass",
        type="motor",
        color_code="#E0C28A",
        sort_order=5,
    )
    assert valid_finish.type == "motor"
    print("✅ Gate 2.1: Valid finish parsed successfully.")

    try:
        FinishCreate(name="Bad Type", type="invalid_type")  # type: ignore
        assert False, "Expected error on invalid finish type"
    except ValidationError:
        print("✅ Gate 2.2: Invalid finish type rejected by Pydantic.")

    # 3. Gate 3: FanProduct Validation
    valid_product = FanProductCreate(
        product_code="FAN-EXP01",
        name="AeroSculpt Ultra",
        description="Sculptural minimalist architecture fan.",
        status="active",
        specifications=valid_specs,
        blade_finish_ids=[str(uuid.uuid4())],
        motor_finish_ids=[str(uuid.uuid4())],
    )
    assert valid_product.status == "active"
    print("✅ Gate 3.1: Valid FanProduct parsed successfully.")

    try:
        FanProductCreate(
            product_code="FAN-BAD",
            name="Bad Status Fan",
            status="archived",  # type: ignore
            specifications=valid_specs,
        )
        assert False, "Expected error on invalid product status"
    except ValidationError:
        print("✅ Gate 3.2: Invalid product status rejected by Pydantic.")

    # 4. Gate 4: FanVariant Model Validation
    var = FanVariant(
        product_id=str(uuid.uuid4()),
        motor_finish_id=str(uuid.uuid4()),
        blade_finish_id=str(uuid.uuid4()),
        sku="SKU-EXP-01",
        is_active=True,
    )
    assert var.is_active is True
    print("✅ Gate 4: FanVariant valid configuration model verified.")

    # 5. Gate 5: AI Job State Machine Validation
    valid_job = AIJob(
        product_id=str(uuid.uuid4()),
        variant_id=str(uuid.uuid4()),
        input_room_image_url="https://example.com/room.jpg",
        status="QUEUED",
    )
    assert valid_job.status == "QUEUED"
    print("✅ Gate 5: Valid AIJob state parsed.")

    print("==================================================")
    print("🎉 ALL DOMAIN MODEL VALIDATION GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_models_verification()
