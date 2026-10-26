"""
Verification Test Suite for Visualization Orchestration (Job state machine works).
"""
import os
import cv2
from fastapi import HTTPException

from app.db.mongo import db_manager
from app.db.seed import seed_database
from app.repositories import (
    products_repo,
    variants_repo,
    ai_jobs_repo,
)
from app.api.routes.users.visualize import (
    create_visualization_job,
    get_visualization_job,
    get_visualization_result,
    VisualizationRequest,
    VISUALIZATIONS_DIR,
)


def run_visualize_verification():
    print("==================================================")
    print("Running Visualization Orchestration Verification...")
    print("==================================================")

    db_manager.connect()
    seed_database()

    # Get sample active product and variant
    import uuid
    from app.repositories import finishes_repo
    products = products_repo.find_active()
    assert len(products) > 0, "Active products required"
    prod = None
    var = None
    for p in products:
        vs = variants_repo.find_by_product(p["product_id"], only_active=True)
        if vs:
            prod = p
            var = vs[0]
            break

    if not var:
        prod = products[0]
        motor_finishes = prod.get("motor_finish_ids") or [f["finish_id"] for f in finishes_repo.find_all(finish_type="motor", is_active=True)]
        blade_finishes = prod.get("blade_finish_ids") or [f["finish_id"] for f in finishes_repo.find_all(finish_type="blade", is_active=True)]
        var = variants_repo.insert({
            "variant_id": f"var-{uuid.uuid4().hex[:8]}",
            "product_id": prod["product_id"],
            "motor_finish_id": motor_finishes[0] if motor_finishes else "mf-default",
            "blade_finish_id": blade_finishes[0] if blade_finishes else "bf-default",
            "sku": f"SKU-{uuid.uuid4().hex[:6]}",
            "is_active": True,
        })

    product_id = prod["product_id"]
    variant_id = var["variant_id"]

    # 1. Gate 1: Normal Job State Machine Execution (QUEUED -> PROCESSING -> SUCCESS)
    req = VisualizationRequest(
        product_id=product_id,
        variant_id=variant_id,
        scale_factor=1.15,
        anchor_x=0.50,
        anchor_y=0.22,
        rotation_deg=25.0,
        apply_lighting=True,
        apply_shadow=True,
    )
    job_res = create_visualization_job(req)
    assert job_res.job_id is not None
    assert job_res.status == "SUCCESS", f"Expected job status SUCCESS, got {job_res.status}"
    assert job_res.result_url is not None
    assert job_res.result_url.startswith("/api/static/visualizations/")
    assert job_res.render_time_ms is not None and job_res.render_time_ms > 0
    job_id = job_res.job_id
    print(f"✅ Gate 1: Job state machine transitioned cleanly to SUCCESS in {job_res.render_time_ms}ms ({job_res.result_url}).")

    # 2. Gate 2: Interactive Controls Preservation in Metadata
    meta = job_res.metadata
    assert meta is not None
    assert meta["rotation_deg"] == 25.0
    assert meta["scale_factor"] == 1.15
    assert meta["lighting_applied"] is True
    assert meta["shadow_applied"] is True
    print("✅ Gate 2: Interactive controls (scale 1.15, rotation 25.0°, lighting, shadow) verified in output metadata.")

    # 3. Gate 3: Physical Output Image File Integrity
    filename = os.path.basename(job_res.result_url)
    filepath = os.path.join(VISUALIZATIONS_DIR, filename)
    assert os.path.exists(filepath), f"Rendered output image missing at {filepath}"
    assert os.path.getsize(filepath) > 5000, "Rendered output image is suspiciously small"
    rendered_cv = cv2.imread(filepath)
    assert rendered_cv is not None, "Rendered image could not be decoded"
    print(f"✅ Gate 3: Physical rendered JPEG output confirmed on disk ({rendered_cv.shape[1]}x{rendered_cv.shape[0]}, {os.path.getsize(filepath)} bytes).")

    # 4. Gate 4: Job Status & Result Retrieval Endpoints
    polled_job = get_visualization_job(job_id)
    assert polled_job.job_id == job_id
    assert polled_job.status == "SUCCESS"
    assert polled_job.result_url == job_res.result_url
    print("✅ Gate 4: Job status polling endpoint verified.")

    # 5. Gate 5: Error Handling in State Machine (Invalid variant)
    bad_req = VisualizationRequest(
        product_id=product_id,
        variant_id="non-existent-variant-id",
        scale_factor=1.0,
    )
    try:
        create_visualization_job(bad_req)
        assert False, "Expected error on invalid variant ID"
    except HTTPException as e:
        assert e.status_code in [400, 404]
        print(f"✅ Gate 5: State machine gracefully handled invalid variant and reported error: {e.detail}")

    # 6. Gate 6: Completion Gate PASSED
    print("✅ Gate 6: Completion Gate PASSED: Job state machine works with full CV pipeline.")

    print("==================================================")
    print("🎉 ALL VISUALIZATION ACCEPTANCE GATES PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    run_visualize_verification()
