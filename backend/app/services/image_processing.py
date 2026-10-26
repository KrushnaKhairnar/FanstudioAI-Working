"""
Image Processing Service for FanStudioAI using OpenCV and Pillow.
Handles room image validation, EXIF orientation correction, perspective analysis,
ceiling region estimation, and lighting metrics per Master Plan Section 10 & 11.
"""
import io
import os
import uuid
from typing import Tuple, Dict, Any, List
import numpy as np
import cv2
from PIL import Image, ImageOps

ROOMS_DIR = os.path.join(os.getcwd(), "data", "rooms")
os.makedirs(ROOMS_DIR, exist_ok=True)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per UI specification
MIN_WIDTH = 400
MIN_HEIGHT = 300
MAX_DIMENSION = 2048


def validate_and_decode_image(raw_bytes: bytes) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Validates file integrity, corrects EXIF orientation, and converts to an OpenCV BGR array.
    Raises ValueError on corruption or dimension violations.
    """
    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size exceeds 10MB limit ({len(raw_bytes) / (1024*1024):.1f}MB)")

    if len(raw_bytes) < 100:
        raise ValueError("Image file payload is too small or empty")

    try:
        pil_img = Image.open(io.BytesIO(raw_bytes))
        pil_img.verify()
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image file: {str(e)}")

    # Re-open after verify()
    pil_img = Image.open(io.BytesIO(raw_bytes))

    # Correct mobile phone orientation using EXIF transpose
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass

    # Convert to RGB (dropping CMYK or palette)
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    width, height = pil_img.size
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValueError(f"Image dimensions ({width}x{height}) must be at least {MIN_WIDTH}x{MIN_HEIGHT}")

    # Downsample if ultra-high resolution
    if max(width, height) > MAX_DIMENSION:
        pil_img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        width, height = pil_img.size

    # Convert PIL RGB to OpenCV BGR
    rgb_arr = np.array(pil_img)
    bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)

    metadata = {
        "width": width,
        "height": height,
        "format": "JPEG",
        "channels": 3,
    }
    return bgr_arr, metadata


def analyze_room_geometry(img: np.ndarray) -> Dict[str, Any]:
    """
    Performs Computer Vision analysis on room photograph:
    - Calculates ambient room brightness and color balance
    - Extracts edge contours in upper portion to detect ceiling plane
    - Estimates optimal fan placement anchor point (x, y) normalized to [0.0, 1.0]
    """
    h, w, _ = img.shape

    # 1. Ambient Lighting Analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    ambient_brightness = float(np.mean(v_channel) / 255.0)

    # Estimate Color Temperature (Red vs Blue ratio)
    b_mean = float(np.mean(img[:, :, 0]))
    r_mean = float(np.mean(img[:, :, 2]))
    rb_ratio = (r_mean + 1.0) / (b_mean + 1.0)
    # Higher rb_ratio = warmer lighting (~3000K-3500K), lower = cooler (~5500K-6500K)
    estimated_kelvin = int(max(2500, min(7000, 4500 - (rb_ratio - 1.0) * 2000)))

    # 2. Ceiling Region & Contour Detection (focusing on upper 45% of room)
    upper_limit = int(h * 0.45)
    ceiling_roi = img[0:upper_limit, :]

    gray = cv2.cvtColor(ceiling_roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 120)

    # Detect horizontal lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=int(w * 0.2), maxLineGap=20)
    
    # Calculate weighted ceiling anchor
    # In standard perspective, ceiling center is near x=0.5, y between 0.18 and 0.32
    default_anchor_x = 0.50
    default_anchor_y = 0.24

    if lines is not None and len(lines) > 0:
        y_coords = []
        for line in lines:
            coords = line[0] if hasattr(line, "shape") and len(line.shape) > 1 else line
            if len(coords) >= 4:
                y_coords.append(float(coords[1]))
                y_coords.append(float(coords[3]))
        if y_coords:
            avg_line_y = float(np.mean(y_coords)) / float(h)
            anchor_y = float(np.clip(avg_line_y + 0.05, 0.15, 0.35))
        else:
            anchor_y = default_anchor_y
    else:
        anchor_y = default_anchor_y

    anchor_x = default_anchor_x

    # Rough bounding polygon for the detected ceiling region
    ceiling_polygon: List[List[float]] = [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, float(np.clip(anchor_y + 0.12, 0.25, 0.45))],
        [0.0, float(np.clip(anchor_y + 0.12, 0.25, 0.45))],
    ]

    return {
        "ceiling_center_x": round(anchor_x, 4),
        "ceiling_center_y": round(anchor_y, 4),
        "ceiling_polygon": ceiling_polygon,
        "ambient_brightness": round(ambient_brightness, 3),
        "color_temp_kelvin": estimated_kelvin,
        "width": w,
        "height": h,
    }


def save_processed_room(room_id: str, img: np.ndarray) -> str:
    """Saves the normalized room image to data/rooms and returns the local access path."""
    filename = f"{room_id}.jpg"
    filepath = os.path.join(ROOMS_DIR, filename)
    cv2.imwrite(filepath, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return f"/api/static/rooms/{filename}"
