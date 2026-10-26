"""
Perspective Transformation & Lighting Adaptation Pipeline.
Applies geometric scaling, affine rotation, perspective vanishing-point warping,
ambient color-temperature matching, soft ceiling drop-shadow synthesis, and seamless alpha compositing.
Adheres strictly to Master Development Plan Section 10 & 11.
"""
from typing import Tuple, Dict, Any, Optional
import numpy as np
import cv2
from PIL import Image


def apply_lighting_and_color_temperature(
    fan_bgr: np.ndarray,
    ambient_brightness: float,
    color_temp_kelvin: int,
) -> np.ndarray:
    """
    Adjusts fan cutout chromatic balance and brightness to harmonize with the room's ambient light.
    - Matches room color temperature (warmer tones for low kelvin, cooler for high kelvin).
    - Harmonizes brightness levels so the fan does not appear artificially glowing or dark.
    """
    # 1. Color temperature adjustment
    # Reference neutral is 5000K.
    temp_diff = (color_temp_kelvin - 5000) / 2500.0  # -1.0 (warm) to +1.0 (cool)
    
    # Gain factors for B, G, R
    b_gain = float(np.clip(1.0 + temp_diff * 0.15, 0.82, 1.20))
    g_gain = 1.0
    r_gain = float(np.clip(1.0 - temp_diff * 0.15, 0.82, 1.20))

    adjusted = fan_bgr.astype(np.float32)
    adjusted[:, :, 0] *= b_gain  # Blue
    adjusted[:, :, 1] *= g_gain  # Green
    adjusted[:, :, 2] *= r_gain  # Red

    # 2. Ambient brightness harmonization
    # Room brightness is typically 0.3 - 0.9. Standard reference is 0.65.
    brightness_factor = float(np.clip(ambient_brightness / 0.65, 0.75, 1.25))
    adjusted *= brightness_factor

    return np.clip(adjusted, 0, 255).astype(np.uint8)


def generate_ceiling_drop_shadow(
    alpha_mask: np.ndarray,
    shadow_blur_ksize: int = 35,
    shadow_opacity: float = 0.40,
    offset_y: int = 15,
) -> Tuple[np.ndarray, int, int]:
    """
    Synthesizes a soft diffuse contact/drop-shadow for the fan on the ceiling plane.
    Returns blurred float32 shadow mask [0.0 - 1.0] and spatial offsets.
    """
    # Dilate and blur the alpha mask to simulate diffuse light occlusion on the ceiling
    ksize = shadow_blur_ksize if shadow_blur_ksize % 2 == 1 else shadow_blur_ksize + 1
    blurred = cv2.GaussianBlur(alpha_mask, (ksize, ksize), 0)
    shadow_float = (blurred.astype(np.float32) / 255.0) * shadow_opacity
    return shadow_float, 0, offset_y


def transform_and_composite_fan(
    room_bgr: np.ndarray,
    fan_rgba: np.ndarray,
    anchor_x_ratio: float = 0.50,
    anchor_y_ratio: float = 0.24,
    scale_factor: float = 1.0,
    rotation_deg: float = 0.0,
    perspective_pitch: float = 0.0,
    ambient_brightness: float = 0.65,
    color_temp_kelvin: int = 4500,
    apply_lighting: bool = True,
    apply_shadow: bool = True,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Main Computer Vision Compositing Engine.
    Transforms fan cutout to match ceiling perspective, adapts lighting, synthesizes shadow,
    and blends seamlessly onto the room photograph.
    """
    room_h, room_w, _ = room_bgr.shape
    fan_h, fan_w, fan_ch = fan_rgba.shape

    if fan_ch != 4:
        raise ValueError(f"Fan cutout image must have 4 channels (RGBA), received {fan_ch}")

    # 1. Base Target Sizing: Fan diameter typically spans ~35% - 45% of room width at scale=1.0
    target_fan_width = int(room_w * 0.40 * scale_factor)
    aspect_ratio = fan_h / float(fan_w)
    target_fan_height = int(target_fan_width * aspect_ratio)

    if target_fan_width < 20 or target_fan_height < 20:
        raise ValueError("Calculated fan target size is too small for rendering")

    resized_fan = cv2.resize(fan_rgba, (target_fan_width, target_fan_height), interpolation=cv2.INTER_LANCZOS4)

    # 2. Affine Rotation & Perspective Pitch
    # Rotate around center
    center = (target_fan_width // 2, target_fan_height // 2)
    rot_mat = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
    
    # Slight perspective pitch (foreshortening the vertical axis to match ceiling perspective tilt)
    # If perspective_pitch != 0, scale Y slightly relative to ceiling horizon
    pitch_scale = float(np.clip(1.0 - abs(perspective_pitch) * 0.015, 0.70, 1.10))
    rot_mat[1, :] *= pitch_scale

    rotated_fan = cv2.warpAffine(
        resized_fan,
        rot_mat,
        (target_fan_width, target_fan_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )

    # Separate BGR and Alpha channels
    fan_bgr = rotated_fan[:, :, :3]
    fan_alpha = rotated_fan[:, :, 3]

    # 3. Ambient Lighting & Color Temperature Harmonization
    if apply_lighting:
        fan_bgr = apply_lighting_and_color_temperature(
            fan_bgr,
            ambient_brightness=ambient_brightness,
            color_temp_kelvin=color_temp_kelvin,
        )

    # 4. Placement Coordinates Calculation
    anchor_px_x = int(room_w * anchor_x_ratio)
    anchor_px_y = int(room_h * anchor_y_ratio)

    # Anchor point represents top center of motor mount (canopy)
    # The fan canopy is at the horizontal center, top ~15% of the fan cutout
    canopy_offset_y = int(target_fan_height * 0.15)
    top_left_x = anchor_px_x - (target_fan_width // 2)
    top_left_y = anchor_px_y - canopy_offset_y

    composite = room_bgr.copy()

    # Calculate valid overlap box inside room dimensions
    x1_fan = max(0, -top_left_x)
    y1_fan = max(0, -top_left_y)
    x2_fan = min(target_fan_width, room_w - top_left_x)
    y2_fan = min(target_fan_height, room_h - top_left_y)

    x1_room = max(0, top_left_x)
    y1_room = max(0, top_left_y)
    x2_room = min(room_w, top_left_x + target_fan_width)
    y2_room = min(room_h, top_left_y + target_fan_height)

    if x2_room <= x1_room or y2_room <= y1_room:
        raise ValueError("Fan coordinates are completely outside room boundaries")

    # Crop active regions
    fan_sub_bgr = fan_bgr[y1_fan:y2_fan, x1_fan:x2_fan]
    fan_sub_alpha = (fan_alpha[y1_fan:y2_fan, x1_fan:x2_fan].astype(np.float32) / 255.0)[:, :, np.newaxis]
    room_sub = composite[y1_room:y2_room, x1_room:x2_room].astype(np.float32)

    # 5. Ceiling Drop-Shadow Synthesis
    if apply_shadow:
        shadow_mask, s_dx, s_dy = generate_ceiling_drop_shadow(fan_alpha)
        # Apply shadow slightly above & behind fan
        shadow_y1 = max(0, top_left_y - 10)
        shadow_y2 = min(room_h, shadow_y1 + target_fan_height)
        shadow_x1 = max(0, top_left_x)
        shadow_x2 = min(room_w, shadow_x1 + target_fan_width)

        sh_crop_h = shadow_y2 - shadow_y1
        sh_crop_w = shadow_x2 - shadow_x1
        if sh_crop_h > 0 and sh_crop_w > 0:
            sh_mask_crop = shadow_mask[0:sh_crop_h, 0:sh_crop_w, np.newaxis]
            room_bg_region = composite[shadow_y1:shadow_y2, shadow_x1:shadow_x2].astype(np.float32)
            # Occlusion multiply: background * (1.0 - shadow_factor)
            room_bg_region = room_bg_region * (1.0 - sh_mask_crop)
            composite[shadow_y1:shadow_y2, shadow_x1:shadow_x2] = np.clip(room_bg_region, 0, 255).astype(np.uint8)

    # Refresh room_sub after shadow
    room_sub = composite[y1_room:y2_room, x1_room:x2_room].astype(np.float32)

    # 6. Seamless Alpha Compositing: composite = fan * alpha + background * (1 - alpha)
    blended = (fan_sub_bgr.astype(np.float32) * fan_sub_alpha) + (room_sub * (1.0 - fan_sub_alpha))
    composite[y1_room:y2_room, x1_room:x2_room] = np.clip(blended, 0, 255).astype(np.uint8)

    metadata = {
        "anchor_x_px": anchor_px_x,
        "anchor_y_px": anchor_px_y,
        "rendered_width": target_fan_width,
        "rendered_height": target_fan_height,
        "rotation_deg": rotation_deg,
        "scale_factor": scale_factor,
        "lighting_applied": apply_lighting,
        "shadow_applied": apply_shadow,
        "adapted_color_temp_kelvin": color_temp_kelvin,
        "adapted_ambient_brightness": ambient_brightness,
    }

    return composite, metadata
