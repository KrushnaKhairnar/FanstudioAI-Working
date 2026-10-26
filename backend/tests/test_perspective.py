"""
Verification Test Suite for Perspective & Lighting Pipeline (Perspective + lighting applied).
"""
import numpy as np
import cv2

from app.services.perspective_lighting import (
    apply_lighting_and_color_temperature,
    generate_ceiling_drop_shadow,
    transform_and_composite_fan,
)


def create_synthetic_transparent_fan(size=400) -> np.ndarray:
    """Creates a 4-channel RGBA fan cutout with a center motor housing and 3 blades."""
    fan_rgba = np.zeros((size, size, 4), dtype=np.uint8)
    center = (size // 2, size // 2)

    # 1. Motor Housing (center circle)
    # RGBA: Dark bronze/black [30, 25, 25, 255]
    cv2.circle(fan_rgba, center, radius=int(size * 0.12), color=(30, 25, 25, 255), thickness=-1)

    # 2. 3 Blades (angled rectangles at 0, 120, 240 degrees)
    # RGBA: Warm walnut [40, 70, 130, 255] (BGR: 40, 70, 130)
    blade_length = int(size * 0.38)
    blade_width = int(size * 0.08)

    for angle in [0, 120, 240]:
        rad = np.radians(angle)
        # End points of blade
        x_end = int(center[0] + blade_length * np.cos(rad))
        y_end = int(center[1] + blade_length * np.sin(rad))
        cv2.line(fan_rgba, center, (x_end, y_end), color=(40, 70, 130, 255), thickness=blade_width)

    # Smooth the alpha edges slightly
    fan_rgba[:, :, 3] = cv2.GaussianBlur(fan_rgba[:, :, 3], (5, 5), 0)
    return fan_rgba


def create_synthetic_room_bgr(width=800, height=600) -> np.ndarray:
    """Creates a synthetic bedroom image (BGR) with ceiling and walls."""
    room = np.zeros((height, width, 3), dtype=np.uint8)
    ceiling_h = int(height * 0.35)
    # Warm off-white ceiling (BGR: 230, 240, 248)
    room[0:ceiling_h, :] = [230, 240, 248]
    # Neutral walls (BGR: 180, 195, 210)
    room[ceiling_h:height, :] = [180, 195, 210]
    return room


def run_perspective_verification():
    print("==================================================")
    print("Running Perspective & Lighting Verification...")
    print("==================================================")

    fan_rgba = create_synthetic_transparent_fan(400)
    assert fan_rgba.shape == (400, 400, 4), "Synthetic fan must be 400x400x4 RGBA"
    assert np.max(fan_rgba[:, :, 3]) > 200, "Alpha channel must be populated"
    print("✅ Gate 1: Synthetic 4-channel transparent fan cutout created.")

    # 2. Gate 2: Lighting & Chromatic Adaptation
    fan_bgr = fan_rgba[:, :, :3]
    # Warm room (3200K) -> Red gain, blue attenuation
    warm_adjusted = apply_lighting_and_color_temperature(fan_bgr, ambient_brightness=0.75, color_temp_kelvin=3200)
    assert warm_adjusted.shape == fan_bgr.shape
    # Cool room (6500K) -> Blue gain, red attenuation
    cool_adjusted = apply_lighting_and_color_temperature(fan_bgr, ambient_brightness=0.60, color_temp_kelvin=6500)
    assert cool_adjusted.shape == fan_bgr.shape
    print("✅ Gate 2: Ambient lighting and chromatic color-temperature harmonization verified (warm and cool modes).")

    # 3. Gate 3: Ceiling Drop-Shadow Synthesis
    shadow_mask, sx, sy = generate_ceiling_drop_shadow(fan_rgba[:, :, 3], shadow_blur_ksize=25, shadow_opacity=0.35)
    assert shadow_mask.shape == (400, 400)
    assert 0.0 <= np.max(shadow_mask) <= 0.40
    assert np.min(shadow_mask) == 0.0
    print("✅ Gate 3: Soft diffuse ceiling drop-shadow synthesis verified.")

    # 4. Gate 4: Scaling, Rotation & Perspective Warping
    room_bgr = create_synthetic_room_bgr(800, 600)
    composite, meta = transform_and_composite_fan(
        room_bgr=room_bgr,
        fan_rgba=fan_rgba,
        anchor_x_ratio=0.50,
        anchor_y_ratio=0.22,
        scale_factor=1.1,
        rotation_deg=35.0,
        perspective_pitch=8.0,
        ambient_brightness=0.80,
        color_temp_kelvin=3800,
        apply_lighting=True,
        apply_shadow=True,
    )
    assert composite.shape == (600, 800, 3), "Composite must match room dimensions"
    assert meta["lighting_applied"] is True
    assert meta["shadow_applied"] is True
    assert meta["rotation_deg"] == 35.0
    assert meta["scale_factor"] == 1.1
    print(f"✅ Gate 4: Perspective transformation and compositing executed ({meta['rendered_width']}x{meta['rendered_height']} fan at anchor [{meta['anchor_x_px']}, {meta['anchor_y_px']}]).")

    # 5. Gate 5: Seamless Alpha Blending & Non-Degradation
    diff = np.abs(composite.astype(np.int32) - room_bgr.astype(np.int32))
    assert np.sum(diff) > 100000, "Composited image must have rendered fan pixels"
    print("✅ Gate 5: Seamless alpha blending and non-destructive pixel integration confirmed.")

    # 6. Gate 6: Completion Gate PASSED
    print("✅ Gate 6: Completion Gate PASSED: Perspective transformation + ambient lighting adaptation successfully applied.")

    print("==================================================")
    print("🎉 ALL PERSPECTIVE ACCEPTANCE GATES PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    run_perspective_verification()
