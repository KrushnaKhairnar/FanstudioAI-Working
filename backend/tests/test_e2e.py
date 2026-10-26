"""
Verification Test Suite for End-to-End System Integration & Acceptance Verification.
Exercises the entire lifecycle across Admin Studio, User Catalog, and Computer Vision AI Pipeline.
"""
import os
import uuid
import cv2
import numpy as np
from fastapi import HTTPException

from app.core.config import settings
from app.db.mongo import db_manager
from app.db.seed import seed_database
from app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
    audit_repo,
)
from app.models.specifications import FanSpecifications
from app.models.product import FanProductCreate
from app.models.variant import FanVariantCreate
from app.api.routes.admin.products import create_product, list_products
from app.api.routes.admin.variants import create_variant
from app.api.routes.users.catalog import (
    get_user_products,
    get_user_finishes,
    get_user_product_variants,
    resolve_variant_combination,
    ResolveVariantRequest,
)
from app.api.routes.users.visualize import (
    create_visualization_job,
    VisualizationRequest,
    get_visualization_job,
    VISUALIZATIONS_DIR,
)
from app.services.image_processing import (
    validate_and_decode_image,
    analyze_room_geometry,
    ROOMS_DIR,
)


def run_e2e_verification():
    print("==================================================")
    print("Running End-to-End System Verification...")
    print("==================================================")

    # 1. Connect database and ensure seed
    db_manager.connect()
    seed_database()

    # Gate 1: System Health & Database Connectivity
    assert db_manager.engine_type in ["mongita_persistent", "mongita_memory", "mongodb"]
    products_cnt = products_repo.count()
    finishes_cnt = finishes_repo.count()
    assert products_cnt > 0, "Products collection must have records"
    assert finishes_cnt > 0, "Finishes collection must have records"
    print(f"✅ Gate 1: System health verified (Engine: {db_manager.engine_type}, {products_cnt} products, {finishes_cnt} finishes).")

    # Gate 2: User Storefront Catalog & Finishes
    user_prods = get_user_products()
    assert len(user_prods) > 0, "User catalog must return active products"
    sample_prod = user_prods[0]
    prod_id = sample_prod.product_id

    all_finishes = get_user_finishes()
    assert len(all_finishes) >= 4, "User finishes must contain baseline finishes"
    motor_finishes = [f for f in all_finishes if f.type == "motor"]
    blade_finishes = [f for f in all_finishes if f.type == "blade"]
    assert len(motor_finishes) > 0 and len(blade_finishes) > 0
    print(f"✅ Gate 2: User storefront catalog verified ({len(user_prods)} active products, {len(motor_finishes)} motor finishes, {len(blade_finishes)} blade finishes).")

    # Gate 3: Live Variant Resolution API
    prod_variants = get_user_product_variants(prod_id)
    assert len(prod_variants) > 0, "Product must have manufactured variants"
    valid_var = prod_variants[0]

    resolve_data = resolve_variant_combination(
        prod_id,
        ResolveVariantRequest(
            motor_finish_id=valid_var.motor_finish_id,
            blade_finish_id=valid_var.blade_finish_id,
        ),
    )
    assert resolve_data.is_valid is True
    res_var_id = resolve_data.variant.get("variant_id") if isinstance(resolve_data.variant, dict) else resolve_data.variant.variant_id
    assert res_var_id == valid_var.variant_id
    print("✅ Gate 3: Interactive finish combination resolver validated.")

    # Gate 4: Admin Product Creation with Specification Integrity (Direct without auth)
    test_code = f"E2E-{uuid.uuid4().hex[:6].upper()}"
    new_product = create_product(
        FanProductCreate(
            product_code=test_code,
            name="E2E Aerodynamic Ceiling Fan",
            description="High-efficiency BLDC motor with hand-balanced sculpted timber blades.",
            specifications=FanSpecifications(
                category="Architectural",
                blade_type="Solid Hardwood",
                blade_count=3,
                motor_type="DC / BLDC Inverter",
            ),
            motor_finish_ids=[motor_finishes[0].finish_id],
            blade_finish_ids=[blade_finishes[0].finish_id],
            status="active",
        )
    )
    new_prod_id = new_product.product_id

    # Register variant
    new_variant = create_variant(
        new_prod_id,
        FanVariantCreate(
            product_id=new_prod_id,
            motor_finish_id=motor_finishes[0].finish_id,
            blade_finish_id=blade_finishes[0].finish_id,
            sku=f"{test_code}-M1B1",
            price_adjustment=0.0,
        )
    )
    print("✅ Gate 4: Admin product & variant matrix registration verified (no auth required).")

    # Gate 5: Room Photo Upload & OpenCV Geometry Detection
    synthetic_room = np.full((600, 800, 3), 235, dtype=np.uint8)
    cv2.line(synthetic_room, (0, 160), (800, 160), (190, 190, 190), 2)
    _, room_buf = cv2.imencode(".jpg", synthetic_room)

    validated_img, meta = validate_and_decode_image(room_buf.tobytes())
    geom = analyze_room_geometry(validated_img)
    anchor_x = geom["ceiling_center_x"]
    anchor_y = geom["ceiling_center_y"]
    assert 0.0 < anchor_x < 1.0
    assert 0.0 < anchor_y < 1.0
    print(f"✅ Gate 5: Room upload and OpenCV geometry analysis verified (anchor: {anchor_x:.2f}, {anchor_y:.2f}).")

    # Gate 6: AI Visualization Job Execution
    vis_job = create_visualization_job(
        VisualizationRequest(
            product_id=new_prod_id,
            variant_id=new_variant.variant_id,
            scale_factor=1.1,
            rotation_deg=15.0,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            apply_lighting=True,
            apply_shadow=True,
        )
    )
    assert vis_job.status == "SUCCESS"
    assert vis_job.result_url is not None
    print(f"✅ Gate 6: AI Computer Vision compositing state machine executed in {vis_job.render_time_ms}ms ({vis_job.result_url}).")

    # Gate 7: Rendered Artifact File Verification
    vis_filename = os.path.basename(vis_job.result_url)
    vis_path = os.path.join(VISUALIZATIONS_DIR, vis_filename)
    assert os.path.exists(vis_path), f"Composited visualization missing at {vis_path}"
    assert os.path.getsize(vis_path) > 2000, "Composited image size suspiciously small"
    decoded = cv2.imread(vis_path)
    assert decoded is not None, "Composited image failed OpenCV decoding"
    print(f"✅ Gate 7: Physical output JPEG integrity confirmed ({decoded.shape[1]}x{decoded.shape[0]} px, {os.path.getsize(vis_path)} bytes).")

    # Gate 8: Comprehensive Audit Trail Logging
    recent_logs = audit_repo.find_recent(limit=10)
    assert len(recent_logs) > 0
    actions = [log["action"] for log in recent_logs]
    assert "CREATE_PRODUCT" in actions or "CREATE_VARIANT" in actions
    print(f"✅ Gate 8: Enterprise audit trail confirmed ({len(recent_logs)} recent audit entries).")

    # Gate 9: Completion Gate PASSED
    print("✅ Gate 9: Completion Gate PASSED: End-to-End System Integration Verified.")

    print("==================================================")
    print("🎉 ALL END-TO-END ACCEPTANCE GATES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_e2e_verification()
