"""
Verification Test Suite for Room Upload & OpenCV Preprocessing (Image validation + preprocessed).
"""
import io
import os
import base64
import numpy as np
from PIL import Image
from fastapi import HTTPException

from app.db.mongo import db_manager
from app.services.image_processing import (
    validate_and_decode_image,
    analyze_room_geometry,
    save_processed_room,
    ROOMS_DIR,
)
from app.api.routes.users.rooms import (
    upload_room_base64,
    get_room,
    Base64UploadRequest,
)


def create_synthetic_room_image(width=800, height=600) -> bytes:
    """Creates a synthetic bedroom image with ceiling, walls, and lighting gradient."""
    # Top 30% is warm off-white ceiling, bottom 70% is bedroom walls & interior
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Ceiling (warm white: 245, 240, 230)
    ceiling_h = int(height * 0.32)
    arr[0:ceiling_h, :] = [245, 240, 230]

    # Crown molding edge line
    arr[ceiling_h - 2 : ceiling_h + 2, :] = [180, 170, 160]

    # Walls (warm neutral: 210, 195, 180)
    arr[ceiling_h:height, :] = [210, 195, 180]

    pil_img = Image.fromarray(arr)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def run_room_upload_verification():
    print("==================================================")
    print("Running Room Upload & OpenCV Verification...")
    print("==================================================")

    db_manager.connect()

    # 1. Gate 1: Reject Corrupted / Empty Images
    try:
        validate_and_decode_image(b"not-an-image-data-corrupted")
        assert False, "Expected ValueError on corrupted image bytes"
    except ValueError as e:
        print(f"✅ Gate 1: Corrupted image properly rejected: {e}")

    # 2. Gate 2: Enforce Minimum Dimensions (< 400x300)
    tiny_img = Image.new("RGB", (200, 150), color=(255, 255, 255))
    tiny_buf = io.BytesIO()
    tiny_img.save(tiny_buf, format="JPEG")
    try:
        validate_and_decode_image(tiny_buf.getvalue())
        assert False, "Expected ValueError on sub-minimum image dimensions"
    except ValueError as e:
        print(f"✅ Gate 2: Sub-minimum dimensions rejected: {e}")

    # 3. Gate 3: Valid Room Image Decoding & Normalization
    room_bytes = create_synthetic_room_image(800, 600)
    cv_bgr, meta = validate_and_decode_image(room_bytes)
    assert cv_bgr is not None
    assert meta["width"] == 800
    assert meta["height"] == 600
    assert cv_bgr.shape == (600, 800, 3)
    print(f"✅ Gate 3: Room image successfully validated and decoded ({meta['width']}x{meta['height']} BGR array).")

    # 4. Gate 4: OpenCV Geometric and Lighting Analysis
    analysis = analyze_room_geometry(cv_bgr)
    assert 0.0 <= analysis["ambient_brightness"] <= 1.0
    assert 2500 <= analysis["color_temp_kelvin"] <= 7500
    assert 0.15 <= analysis["ceiling_center_y"] <= 0.35, f"Ceiling anchor Y {analysis['ceiling_center_y']} out of bounds"
    assert len(analysis["ceiling_polygon"]) == 4, "Ceiling polygon must have 4 bounding vertices"
    print(f"✅ Gate 4: OpenCV analysis calculated ceiling anchor ({analysis['ceiling_center_x']}, {analysis['ceiling_center_y']}), brightness {analysis['ambient_brightness']}, and color temp {analysis['color_temp_kelvin']}K.")

    # 5. Gate 5: Preprocessed Image Persistence
    test_room_id = "test-room-phase10"
    saved_url = save_processed_room(test_room_id, cv_bgr)
    expected_path = os.path.join(ROOMS_DIR, f"{test_room_id}.jpg")
    assert os.path.exists(expected_path), f"Processed image file not found at {expected_path}"
    assert os.path.getsize(expected_path) > 1000, "Saved image file is suspiciously small"
    print(f"✅ Gate 5: Preprocessed image persisted to disk ({saved_url}).")

    # 6. Gate 6: Room Upload via Base64 API Endpoint
    b64_str = f"data:image/jpeg;base64,{base64.b64encode(room_bytes).decode('utf-8')}"
    res = upload_room_base64(Base64UploadRequest(image_base64=b64_str, filename="master_bedroom.jpg"))
    assert res.room_id is not None
    assert res.image_url.startswith("/api/static/rooms/")
    assert res.width == 800
    assert res.height == 600
    assert res.analysis.ceiling_center_y > 0.15
    uploaded_room_id = res.room_id
    print("✅ Gate 6: Room uploaded and preprocessed via API endpoint successfully.")

    # 7. Gate 7: Room Metadata Retrieval
    retrieved = get_room(uploaded_room_id)
    assert retrieved.room_id == uploaded_room_id
    assert retrieved.image_url == res.image_url
    print("✅ Gate 7: Room metadata retrieval verified from database.")

    print("==================================================")
    print("🎉 ALL ROOM UPLOAD ACCEPTANCE GATES PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    run_room_upload_verification()
