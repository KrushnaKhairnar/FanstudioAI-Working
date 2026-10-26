#!/usr/bin/env python3
"""
Generates clean, transparent background PNG cutouts for all ceiling fan images
in uploads/fans/<FAN_NAME>/ using ImageMagick floodfill.
"""

import os
import subprocess
import glob

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FANS_DIR = os.path.join(ROOT_DIR, "uploads", "fans")

print(f"🔍 Scanning '{FANS_DIR}' for ceiling fan images...")

image_extensions = (".jpg", ".jpeg", ".png", ".webp")
processed = 0
skipped = 0
errors = 0

for root, dirs, files in os.walk(FANS_DIR):
    for f in files:
        # Avoid re-processing transparent cutouts
        if f.endswith("_transparent.png") or f.endswith("_cutout.png"):
            continue

        base, ext = os.path.splitext(f)
        if ext.lower() not in image_extensions:
            continue

        src_path = os.path.join(root, f)
        out_path = os.path.join(root, f"{base}_transparent.png")

        try:
            # Floodfill transparency starting from perimeter with 12% fuzz tolerance
            cmd = [
                "convert", src_path,
                "-bordercolor", "white", "-border", "1x1",
                "-fuzz", "12%", "-fill", "none", "-floodfill", "+0+0", "white",
                "-shave", "1x1",
                out_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(out_path):
                processed += 1
                if processed % 15 == 0:
                    print(f"  ✓ Processed {processed} cutouts... ({f})")
            else:
                errors += 1
                print(f"  ⚠️ Warning for {f}: {res.stderr.strip()[:100]}")
        except Exception as e:
            errors += 1
            print(f"  ❌ Error processing {f}: {e}")

print(f"\n🎉 Background removal complete!")
print(f"  • Total transparent cutouts generated: {processed}")
print(f"  • Errors: {errors}")
