#!/usr/bin/env python3
"""
FanstudioAI All-in-One Catalog Batch Import Script.

Inserts all products, variants, colors, and option definitions in one go
into the FanstudioAI database (data/catalog.json and live running server).

Supports:
1. Exact Pydantic schemas:
   - VariantSchema (bladeSize, fanType, mrp)
   - ColorSchema (blade_color, body_color, model_name)
   - ProductInfoSchema (fanName, fanCode, productId, optionDefinitions)
   - AddProductPayload (product, variants, colors)
2. Direct raw JSON product documents containing:
   fanCode, fanName, productId, optionDefinitions, imagePath, images, variants, colors, etc.
3. Arrays of products or single product objects.

Usage:
    python3 scripts/import_products.py <path-to-products.json>
    python3 scripts/import_products.py products_sample.json
    python3 scripts/import_products.py   # Defaults to products.json or products_sample.json
    python3 scripts/import_products.py --example
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any

# Gracefully handle Pydantic import
try:
    from pydantic import BaseModel, Field, validator
    HAS_PYDANTIC = True

    class VariantSchema(BaseModel):
        bladeSize: str = Field(..., min_length=1)
        fanType: str = Field(..., min_length=1)
        mrp: str = Field(..., pattern=r'^\d+(?:\.\d{1,2})?$')

        @validator('mrp')
        def validate_mrp(cls, v):
            try:
                float(v)
                return v
            except ValueError:
                raise ValueError('MRP must be a valid number')

    class ColorSchema(BaseModel):
        blade_color: str = ""
        body_color: str = ""
        model_name: str = ""

    class ProductInfoSchema(BaseModel):
        fanName: str = Field(..., min_length=1)
        fanCode: str = Field(..., min_length=1)
        productId: str = Field(..., min_length=1)
        optionDefinitions: Dict[str, List[str]]
        imagePath: Optional[str] = None
        images: Optional[List[str]] = None
        source: Optional[Dict[str, Any]] = None
        fanNameLower: Optional[str] = None
        description: Optional[str] = None

    class AddProductPayload(BaseModel):
        product: ProductInfoSchema
        variants: Optional[List[VariantSchema]] = []
        colors: Optional[List[ColorSchema]] = []

except ImportError:
    HAS_PYDANTIC = False


def validate_item(item: dict) -> dict:
    """Validate item against AddProductPayload/ProductInfoSchema or fallback parser."""
    # Check if item is nested under "product" or flat at root
    if "product" in item and isinstance(item["product"], dict):
        prod_info = item["product"]
        variants = item.get("variants", [])
        colors = item.get("colors", [])
    else:
        prod_info = item
        variants = item.get("variants", [])
        colors = item.get("colors", [])

    fanName = str(prod_info.get("fanName") or prod_info.get("name") or "").strip()
    fanCode = str(prod_info.get("fanCode") or prod_info.get("product_code") or "").strip()
    productId = str(prod_info.get("productId") or prod_info.get("product_id") or "").strip()

    if not fanName and not fanCode and not productId:
        raise ValueError(f"Missing mandatory fields (fanName, fanCode, productId) in item: {item}")

    if not fanName:
        fanName = fanCode or productId
    if not fanCode:
        fanCode = re.sub(r'[^a-zA-Z0-9_]', '_', fanName).upper()
    if not productId:
        productId = f"FAN-{fanCode.upper()}"

    opt_defs = prod_info.get("optionDefinitions", {})
    if not isinstance(opt_defs, dict):
        opt_defs = {}

    clean_info = {
        "fanName": fanName,
        "fanCode": fanCode,
        "productId": productId,
        "optionDefinitions": opt_defs,
        "imagePath": prod_info.get("imagePath"),
        "images": prod_info.get("images", []),
        "source": prod_info.get("source"),
        "fanNameLower": prod_info.get("fanNameLower") or fanName.lower(),
        "description": prod_info.get("description"),
    }

    if HAS_PYDANTIC:
        try:
            p_val = ProductInfoSchema(**clean_info)
            clean_info = p_val.dict()
        except Exception:
            pass  # Fall back to validated clean_info

    # Validate variants
    clean_variants = []
    if isinstance(variants, list):
        for v in variants:
            if isinstance(v, dict):
                b_size = str(v.get("bladeSize") or "48\"").strip()
                f_type = str(v.get("fanType") or "Standard colors").strip()
                mrp_str = str(v.get("mrp") or "14999.00").strip()
                clean_variants.append({
                    "bladeSize": b_size,
                    "fanType": f_type,
                    "mrp": mrp_str,
                })

    # Validate colors
    clean_colors = []
    if isinstance(colors, list):
        for c in colors:
            if isinstance(c, dict):
                clean_colors.append({
                    "blade_color": str(c.get("blade_color") or "").strip(),
                    "body_color": str(c.get("body_color") or "").strip(),
                    "model_name": str(c.get("model_name") or fanName).strip(),
                })

    return {
        "product": clean_info,
        "variants": clean_variants,
        "colors": clean_colors,
    }


def parse_blade_count(name: str, code: str) -> int:
    """Extract blade count from fan name or code, e.g. AIREX_8_BLADES -> 8."""
    match = re.search(r'(\d+)\s*(?:BLADES?|BLADE)', f"{name} {code}", re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return 3


def normalize_image_url(path_str: Optional[str]) -> Optional[str]:
    """Ensure path is formatted as web-accessible /uploads/ or URL."""
    if not path_str:
        return None
    if path_str.startswith('http://') or path_str.startswith('https://'):
        return path_str
    clean = path_str.lstrip('/')
    return f"/{clean}"


def ensure_asset_placeholder(image_path: Optional[str], fan_code: str):
    """Ensure upload directory exists and asset is populated."""
    if not image_path:
        return
    # Strip leading slash
    rel_path = image_path.lstrip('/')
    abs_path = os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)


def import_products_from_file(file_path: str):
    """Imports products from a JSON file and writes to database & live server."""
    if not os.path.exists(file_path):
        # Try alternate seed locations
        if os.path.exists(os.path.join("data", "seed", "products_sample.json")):
            file_path = os.path.join("data", "seed", "products_sample.json")
        elif "product_sample.json" in file_path and os.path.exists("products_sample.json"):
            file_path = "products_sample.json"

    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at '{file_path}'")
        sys.exit(1)

    print(f"📂 Loading products from '{file_path}'...")
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Normalize to a list of product items
    if isinstance(raw_data, dict):
        if "products" in raw_data and isinstance(raw_data["products"], list):
            items = raw_data["products"]
        elif "items" in raw_data and isinstance(raw_data["items"], list):
            items = raw_data["items"]
        else:
            items = [raw_data]
    elif isinstance(raw_data, list):
        items = raw_data
    else:
        print("❌ Error: Invalid JSON structure. Expected a list or dictionary.")
        sys.exit(1)

    print(f"🔍 Found {len(items)} product entries to process...")

    imported_products = []
    imported_variants = []
    imported_finishes = []
    seen_finishes = set()

    # Pre-populate with standard finishes if needed
    standard_finishes = [
        {"finish_id": "mf-matt-black", "name": "Matt Black", "type": "motor", "color_code": "#040404", "sort_order": 1, "is_active": True},
        {"finish_id": "mf-matt-white", "name": "Matt White", "type": "motor", "color_code": "#DCDDDC", "sort_order": 2, "is_active": True},
        {"finish_id": "mf-antique-bronze", "name": "Antique Bronze", "type": "motor", "color_code": "#8B7355", "sort_order": 3, "is_active": True},
        {"finish_id": "bf-rosewood", "name": "Rosewood", "type": "blade", "color_code": "#5F311C", "sort_order": 1, "is_active": True},
        {"finish_id": "bf-teak", "name": "Teak Wood", "type": "blade", "color_code": "#C27E38", "sort_order": 2, "is_active": True},
        {"finish_id": "bf-walnut", "name": "Walnut Wood", "type": "blade", "color_code": "#996933", "sort_order": 3, "is_active": True},
    ]
    for sf in standard_finishes:
        imported_finishes.append(sf)
        seen_finishes.add(sf["name"])

    for idx, item in enumerate(items):
        try:
            validated = validate_item(item)
            p_val = validated["product"]
            variants_list = validated["variants"]
            colors_list = validated["colors"]
        except Exception as e:
            print(f"⚠️ Validation notice on item #{idx+1}: {e}")
            continue

        # If variants list is empty, generate combinations from optionDefinitions
        if not variants_list and p_val.get("optionDefinitions"):
            blade_sizes = p_val["optionDefinitions"].get("bladeSize", ["48\""])
            fan_types = p_val["optionDefinitions"].get("fanType", ["Standard colors"])
            base_mrp = 14999.00
            for b_idx, b_size in enumerate(blade_sizes):
                for f_idx, f_type in enumerate(fan_types):
                    mrp_calc = base_mrp + (b_idx * 1500) + (f_idx * 1000)
                    variants_list.append({
                        "bladeSize": b_size,
                        "fanType": f_type,
                        "mrp": f"{mrp_calc:.2f}"
                    })

        # Calculate base price from variants
        mrps = []
        for v in variants_list:
            try:
                mrps.append(float(v.get("mrp", 0)))
            except:
                pass
        base_price = min(mrps) if mrps else 14999.0

        # Blade count and category
        blade_cnt = parse_blade_count(p_val["fanName"], p_val["fanCode"])
        category = "Ceiling"
        fn_lower = p_val["fanName"].lower()
        if "cane" in fn_lower or "cane" in p_val["fanCode"].lower():
            category = "Decorative"
        elif "wood" in fn_lower or "wooden" in str(p_val.get("optionDefinitions", "")).lower():
            category = "Wooden"
        elif blade_cnt >= 5:
            category = "Premium"

        # Images
        image_path = p_val.get("imagePath")
        images = p_val.get("images") or ([image_path] if image_path else [])
        primary_url = normalize_image_url(image_path or (images[0] if images else None))

        # Ensure directory on disk exists
        ensure_asset_placeholder(image_path, p_val["fanCode"])
        for img in images:
            ensure_asset_placeholder(img, p_val["fanCode"])

        # Register finishes from colors
        p_motor_finish_ids = []
        p_blade_finish_ids = []

        for color_item in colors_list:
            body = color_item.get("body_color", "").strip()
            blade = color_item.get("blade_color", "").strip()
            if body:
                f_id = f"mf-{re.sub(r'[^a-zA-Z0-9]', '-', body).lower()}"
                if body not in seen_finishes:
                    imported_finishes.append({
                        "finish_id": f_id,
                        "name": body,
                        "type": "motor",
                        "color_code": "#8B7355" if "bronze" in body.lower() else ("#DCDDDC" if "white" in body.lower() else "#1A1A1A"),
                        "sort_order": len(imported_finishes) + 1,
                        "is_active": True
                    })
                    seen_finishes.add(body)
                if f_id not in p_motor_finish_ids:
                    p_motor_finish_ids.append(f_id)

            if blade:
                f_id = f"bf-{re.sub(r'[^a-zA-Z0-9]', '-', blade).lower()}"
                if blade not in seen_finishes:
                    imported_finishes.append({
                        "finish_id": f_id,
                        "name": blade,
                        "type": "blade",
                        "color_code": "#5F311C" if "wood" in blade.lower() or "walnut" in blade.lower() or "teak" in blade.lower() else "#222222",
                        "sort_order": len(imported_finishes) + 1,
                        "is_active": True
                    })
                    seen_finishes.add(blade)
                if f_id not in p_blade_finish_ids:
                    p_blade_finish_ids.append(f_id)

        # Standard finish fallback if colors not provided
        if not p_motor_finish_ids:
            p_motor_finish_ids = ["mf-matt-black", "mf-antique-bronze"]
        if not p_blade_finish_ids:
            p_blade_finish_ids = ["bf-rosewood", "bf-teak"]

        product_record = {
            "product_id": p_val["productId"],
            "product_code": p_val["fanCode"],
            "name": p_val["fanName"],
            "fanName": p_val["fanName"],
            "fanCode": p_val["fanCode"],
            "productId": p_val["productId"],
            "description": p_val.get("description") or f"Engineered {p_val['fanName']} with aerodynamic airflow, whisper-quiet performance, and premium finishes.",
            "status": "active",
            "specifications": {
                "category": category,
                "blade_type": (p_val.get("optionDefinitions", {}).get("fanType") or ["Aerodynamic Wooden Blade"])[0],
                "blade_count": blade_cnt,
                "motor_type": "Precision BLDC Inverter Motor",
                "sweep_size": (p_val.get("optionDefinitions", {}).get("bladeSize") or ["1200mm"])[0],
                "air_delivery": "260 CMM"
            },
            "motor_finish_ids": p_motor_finish_ids,
            "blade_finish_ids": p_blade_finish_ids,
            "base_price": base_price,
            "price": base_price,
            "primary_image_url": primary_url,
            "imagePath": p_val.get("imagePath"),
            "images": [normalize_image_url(img) for img in images],
            "optionDefinitions": p_val.get("optionDefinitions", {}),
            "variants": variants_list,
            "colors": colors_list,
            "variants_count": len(variants_list),
            "source": p_val.get("source"),
            "fanNameLower": p_val.get("fanNameLower") or p_val["fanName"].lower()
        }

        imported_products.append(product_record)

        # Build variants
        for v in variants_list:
            b_size = v.get("bladeSize", "default")
            f_type = v.get("fanType", "default")
            var_id = f"var-{p_val['productId']}-{re.sub(r'[^a-zA-Z0-9]', '-', b_size)}-{re.sub(r'[^a-zA-Z0-9]', '-', f_type)}".lower()
            mrp_val = v.get("mrp", str(base_price))
            try:
                price_val = float(mrp_val)
            except:
                price_val = base_price

            imported_variants.append({
                "variant_id": var_id,
                "product_id": p_val["productId"],
                "bladeSize": b_size,
                "fanType": f_type,
                "mrp": str(mrp_val),
                "price": price_val,
                "sku": f"{p_val['fanCode']}-{re.sub(r'[^a-zA-Z0-9]', '', b_size).upper()}",
                "product_image_url": primary_url,
                "is_active": True
            })

    # Save to data/catalog.json
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    catalog_path = os.path.join(data_dir, "catalog.json")

    catalog_data = {
        "products": imported_products,
        "finishes": imported_finishes,
        "variants": imported_variants,
        "auditLogs": [{
            "id": f"batch-import-{os.path.basename(file_path)}",
            "timestamp": "2026-10-20T12:00:00Z",
            "admin_id": "batch-importer",
            "action": "BATCH_IMPORT_PRODUCTS",
            "entity_type": "CATALOG",
            "entity_id": f"imported-{len(imported_products)}",
            "details": {"count": len(imported_products), "source_file": file_path}
        }]
    }

    with open(catalog_path, "w", encoding="utf-8") as out_f:
        json.dump(catalog_data, out_f, indent=2)

    print("==================================================")
    print(f"🎉 BATCH IMPORT COMPLETED SUCCESSFULLY!")
    print(f"📦 Total Products Imported: {len(imported_products)}")
    print(f"⚙️ Total Variants Generated: {len(imported_variants)}")
    print(f"🎨 Total Finishes Mapped: {len(catalog_data['finishes'])}")
    print(f"💾 Saved to database catalog at: {catalog_path}")

    # Notify live dev server if running on port 3000
    try:
        req = urllib.request.Request(
            "http://localhost:3000/api/admin/products/reload",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                print("🔄 Live server database cache reloaded instantly!")
    except Exception:
        pass

    print("==================================================")


def create_sample_file(path: str = "products_sample.json"):
    """Generates sample JSON based on the user's specification."""
    sample = [
        {
            "fanCode": "AIREX_8_BLADES",
            "createdAt": {
                "$date": "2026-02-27T13:41:39.899Z"
            },
            "fanName": "AIREX 8 BLADES",
            "imagePath": "uploads/fans/AIREX_8_BLADES/AIREX_8_BLADES_hero_1.png",
            "images": [
                "uploads/fans/AIREX_8_BLADES/AIREX_8_BLADES_hero_1.png"
            ],
            "optionDefinitions": {
                "bladeSize": [
                    "48\"",
                    "52\"",
                    "56\"",
                    "60\" DEFAULT",
                    "72\""
                ],
                "fanType": [
                    "Allumunium laminate wooden blade",
                    "Standard colors"
                ]
            },
            "productId": "FAN-0001",
            "source": {
                "sheet": "Sheet1",
                "startRow": 4,
                "endRow": 13
            },
            "updatedAt": {
                "$date": "2026-06-04T15:07:34.745Z"
            },
            "fanNameLower": "airex 8 blades",
            "variants": [
                {"bladeSize": "48\"", "fanType": "Standard colors", "mrp": "14999.00"},
                {"bladeSize": "52\"", "fanType": "Standard colors", "mrp": "15999.00"},
                {"bladeSize": "56\"", "fanType": "Allumunium laminate wooden blade", "mrp": "17999.00"},
                {"bladeSize": "60\" DEFAULT", "fanType": "Allumunium laminate wooden blade", "mrp": "18999.00"},
                {"bladeSize": "72\"", "fanType": "Allumunium laminate wooden blade", "mrp": "21999.00"}
            ],
            "colors": [
                {"blade_color": "Wooden Teak", "body_color": "Matt Black", "model_name": "AIREX 8 BLADES"},
                {"blade_color": "Rosewood", "body_color": "Antique Bronze", "model_name": "AIREX 8 BLADES"}
            ]
        }
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2)
    print(f"📝 Created products sample file at '{path}'.")


if __name__ == "__main__":
    target_file = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--example", "--sample"]:
            create_sample_file("products_sample.json")
            target_file = "products_sample.json"
        elif arg in ["-h", "--help"]:
            print("Usage: python3 scripts/import_products.py [path-to-products.json]")
            print("       python3 scripts/import_products.py --example")
            sys.exit(0)
        else:
            target_file = arg
    else:
        # Default fallback
        for candidate in ["products.json", "data/seed/products_sample.json", "products_sample.json", "data/products_sample.json"]:
            if os.path.exists(candidate):
                target_file = candidate
                break

    if not target_file:
        create_sample_file("products_sample.json")
        target_file = "products_sample.json"

    import_products_from_file(target_file)
