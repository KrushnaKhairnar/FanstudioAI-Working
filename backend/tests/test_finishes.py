"""
Verification Test Suite: Finish Management.
"""
from fastapi import HTTPException

from app.db.mongo import db_manager
from app.db.seed import seed_database
from app.repositories import finishes_repo, audit_repo
from app.models.finish import FinishCreate, FinishUpdate
from app.models.variant import FanVariant
from app.api.routes.admin.finishes import (
    create_finish,
    list_finishes,
    get_finish,
    update_finish,
    update_finish_status,
    deactivate_finish,
    FinishStatusUpdate,
)


def run_finishes_verification():
    print("==================================================")
    print("Running Finish Management Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    # Clean up any prior test finish
    old_f = finishes_repo.find_by_name_and_type("Test Champagne Gold", "motor")
    if old_f:
        finishes_repo.collection.delete_one({"finish_id": old_f["finish_id"]})

    old_b = finishes_repo.find_by_name_and_type("Test Smoked Walnut", "blade")
    if old_b:
        finishes_repo.collection.delete_one({"finish_id": old_b["finish_id"]})

    # 1. Create Motor and Blade Finishes
    motor_payload = FinishCreate(
        name="Test Champagne Gold",
        type="motor",
        color_code="#D4AF37",
        image_url="https://example.com/finishes/champagne-gold.png",
        sort_order=10,
        is_active=True,
    )
    created_motor = create_finish(motor_payload)
    assert created_motor.finish_id is not None
    assert created_motor.name == "Test Champagne Gold"
    assert created_motor.type == "motor"
    motor_id = created_motor.finish_id
    print("✅ Gate 1.1: Motor finish created successfully.")

    blade_payload = FinishCreate(
        name="Test Smoked Walnut",
        type="blade",
        color_code="#3B2F2F",
        image_url="https://example.com/finishes/smoked-walnut.png",
        sort_order=11,
        is_active=True,
    )
    created_blade = create_finish(blade_payload)
    assert created_blade.finish_id is not None
    assert created_blade.type == "blade"
    blade_id = created_blade.finish_id
    print("✅ Gate 1.2: Blade finish created successfully.")

    # 2. Duplicate Prevention
    try:
        create_finish(motor_payload)
        assert False, "Expected 400 on duplicate finish name and type"
    except HTTPException as e:
        assert e.status_code == 400
        print("✅ Gate 2: Duplicate finish rejected with 400.")

    # 3. List Finishes
    motor_list = list_finishes(finish_type="motor", is_active=True)
    for f in motor_list:
        assert f.type == "motor"

    # 4. Get Finish by ID
    fetched_f = get_finish(motor_id)
    assert fetched_f.finish_id == motor_id
    print("✅ Gate 3: Retrieve finish by ID verified.")

    # 5. Update Finish Details
    updated_motor = update_finish(
        motor_id,
        FinishUpdate(color_code="#E0C28A", sort_order=15),
    )
    assert updated_motor.color_code == "#E0C28A"
    print("✅ Gate 4: Update finish verified.")

    # 6. Deactivation Lifecycle
    deactivated = deactivate_finish(motor_id)
    assert deactivated["is_active"] is False
    in_db = finishes_repo.find_by_id(motor_id)
    assert in_db["is_active"] is False

    # Reactivate
    reactivated = update_finish_status(motor_id, FinishStatusUpdate(is_active=True))
    assert reactivated.is_active is True
    print("✅ Gate 5: Deactivation and reactivation verified.")

    print("==================================================")
    print("🎉 ALL FINISH MANAGEMENT GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_finishes_verification()
