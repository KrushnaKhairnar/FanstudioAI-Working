"""
Verification Test Suite: Database Design, Collections, & Index Strategy.
"""
from app.db.mongo import db_manager
from app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
    audit_repo,
)


def run_db_verification():
    print("==================================================")
    print("Running Database & Schema Verification...")
    print("==================================================")

    db_manager.connect()

    # 1. Verify Products Collection
    products = products_repo.find_active()
    assert len(products) >= 2, f"Expected at least 2 active products, found {len(products)}"
    for p in products:
        assert "product_id" in p, "Product must have product_id UUID"
        assert p["status"] == "active", "Public products must have status 'active'"
        assert "specifications" in p or "name" in p, "Product must have specifications or name"
        print(f"  Verified Product: {p.get('name')} ({p.get('product_code')})")
    print("✅ Gate 1 Passed: Products collection verified.")

    # 2. Verify Reusable Finishes Collection
    motor_finishes = finishes_repo.find_all(finish_type="motor", is_active=True)
    blade_finishes = finishes_repo.find_all(finish_type="blade", is_active=True)
    assert len(motor_finishes) >= 4, "Expected at least 4 active motor finishes"
    assert len(blade_finishes) >= 4, "Expected at least 4 active blade finishes"
    print(f"✅ Gate 2 Passed: Reusable Finishes verified ({len(motor_finishes)} motor, {len(blade_finishes)} blade).")

    # 3. Verify Soft-Delete / Deactivation Lifecycle
    sample_prod = products[0]
    test_prod_id = sample_prod["product_id"]
    products_repo.soft_delete_or_deactivate(test_prod_id)
    deactivated = products_repo.find_by_id(test_prod_id)
    assert deactivated["status"] == "inactive", "Product soft-deactivation failed"
    # Restore product
    products_repo.restore(test_prod_id)
    restored = products_repo.find_by_id(test_prod_id)
    assert restored["status"] == "active", "Product restoration failed"
    print("✅ Gate 3 Passed: Soft-delete/deactivation and restoration lifecycle verified.")

    # 4. Verify Audit Trail Logging (no admin identity)
    log_entry = audit_repo.log(
        action="TEST_VERIFICATION",
        target_entity="system",
        target_id="test_db",
        details={"status": "passed"},
    )
    assert log_entry["action"] == "TEST_VERIFICATION", "Audit log failed"
    recent_logs = audit_repo.find_recent(limit=1)
    assert len(recent_logs) > 0, "No audit logs found"
    print("✅ Gate 4 Passed: Audit trail logging verified.")

    print("==================================================")
    print("🎉 ALL DATABASE VERIFICATION GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_db_verification()
