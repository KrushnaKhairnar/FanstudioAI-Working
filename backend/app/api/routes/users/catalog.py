"""
User Catalog API Router.
Provides public access to fan products, finishes, variants, combination images, and transparent cutouts.
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.app.repositories import (
    products_repo,
    finishes_repo,
    variants_repo,
    media_repo,
)
from backend.app.models.product import FanProduct
from backend.app.models.finish import Finish
from backend.app.models.variant import FanVariant
from backend.app.models.media import ProductMedia

router = APIRouter(prefix="/api/users", tags=["User Catalog"])

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
UPLOADS_DIR = ROOT_DIR / "uploads"
DATA_DIR = ROOT_DIR / "data"


class PublicProductSummary(BaseModel):
    product_id: str
    product_code: str
    name: str
    fanName: Optional[str] = None
    fanCode: Optional[str] = None
    productId: Optional[str] = None
    description: Optional[str] = None
    category: str
    blade_type: str
    blade_count: int
    motor_type: str
    primary_image_url: Optional[str] = None
    transparent_image_url: Optional[str] = None
    imagePath: Optional[str] = None
    images: List[str] = []
    
    motor_colors: List[str] = []
    blade_colors: List[str] = []
    default_motor_color: Optional[str] = None
    default_blade_color: Optional[str] = None
    color_combinations: List[Dict[str, Any]] = []
    
    optionDefinitions: Optional[Dict[str, List[str]]] = None
    colors: Optional[List[Dict[str, Any]]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    
    price: float = 12990.0
    variants_count: int = 0
    motor_finish_ids: List[str] = []
    blade_finish_ids: List[str] = []
    tag: Optional[str] = None


class PublicProductDetail(BaseModel):
    product: Dict[str, Any]
    motor_finishes: List[Dict[str, Any]]
    blade_finishes: List[Dict[str, Any]]
    variants: List[Dict[str, Any]]
    media: List[Dict[str, Any]]
    primary_image_url: Optional[str] = None
    price: float = 12990.0


class ResolveVariantRequest(BaseModel):
    motor_finish_id: str = Field(..., description="ID of selected motor finish")
    blade_finish_id: str = Field(..., description="ID of selected blade finish")


class ResolveVariantResponse(BaseModel):
    is_valid: bool
    message: Optional[str] = None
    variant: Optional[Dict[str, Any]] = None


@router.get("/products", response_model=List[PublicProductSummary])
def get_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    blade_count: Optional[int] = None,
    motor_type: Optional[str] = None,
    motor_finish_id: Optional[str] = None,
    blade_finish_id: Optional[str] = None,
    sort_by: str = "popular",
    skip: int = 0,
    limit: int = 200,
):
    """List active catalog products with search and filtering capabilities."""
    all_products = products_repo.find_all(skip=0, limit=500)
    filtered = []
    search_term = search.lower().strip() if search else None

    for p in all_products:
        specs = p.get("specifications", {})
        p_cat = p.get("category") or specs.get("category", "")
        
        if category and category.lower() != "all fans" and category.lower() not in p_cat.lower():
            continue

        bc = p.get("blade_count") or specs.get("blade_count")
        if blade_count is not None and bc != blade_count:
            continue

        if search_term:
            name = (p.get("name") or "").lower()
            code = (p.get("product_code") or p.get("fanCode") or "").lower()
            desc = (p.get("description") or "").lower()
            if (search_term not in name and search_term not in code 
                    and search_term not in desc and search_term not in p_cat.lower()):
                continue

        filtered.append(p)

    if sort_by == "Price: Low to High":
        filtered.sort(key=lambda x: x.get("price") or x.get("base_price", 0))
    elif sort_by == "Price: High to Low":
        filtered.sort(key=lambda x: x.get("price") or x.get("base_price", 0), reverse=True)

    paginated = filtered[skip : skip + limit]
    summaries = []

    for p in paginated:
        specs = p.get("specifications", {})
        p_id = p.get("product_id") or p.get("productId")
        code = p.get("product_code") or p.get("fanCode") or p_id
        
        m_colors = p.get("motor_colors") or []
        b_colors = p.get("blade_colors") or []
        def_m = p.get("default_motor_color") or (m_colors[0] if m_colors else "Matt Grey")
        def_b = p.get("default_blade_color") or (b_colors[0] if b_colors else "Teak Wooden")

        combinations = p.get("color_combinations") or []
        if not combinations and m_colors and b_colors:
            for mc in m_colors:
                m_slug = mc.lower().replace(" ", "-")
                for bc in b_colors:
                    b_slug = bc.lower().replace(" ", "-")
                    combinations.append({
                        "combination_id": f"{code}_{m_slug}_{b_slug}",
                        "motor_color": mc,
                        "blade_color": bc,
                        "image_url": f"/api/users/combination-image?fan_code={code}&motor_color={mc}&blade_color={bc}",
                        "transparent_image_url": f"/api/users/combination-image?fan_code={code}&motor_color={mc}&blade_color={bc}&transparent=true"
                    })

        primary_img = (
            p.get("primary_image_url") 
            or p.get("imagePath")
            or f"/api/users/combination-image?fan_code={code}&motor_color={def_m}&blade_color={def_b}"
        )
        transparent_img = (
            p.get("transparent_image_url")
            or f"/api/users/combination-image?fan_code={code}&motor_color={def_m}&blade_color={def_b}&transparent=true"
        )

        variants_count = len(combinations) if combinations else len(variants_repo.find_by_product(p_id, only_active=True))

        summary = PublicProductSummary(
            product_id=p_id,
            product_code=code,
            name=p.get("name") or p.get("fanName") or "Ceiling Fan",
            fanName=p.get("fanName") or p.get("name"),
            fanCode=code,
            productId=p_id,
            description=p.get("description"),
            category=p.get("category") or specs.get("category", "Ceiling Fan"),
            blade_type=specs.get("blade_type", "Aerodynamic ABS"),
            blade_count=specs.get("blade_count", 3),
            motor_type=specs.get("motor_type", "Energy-Efficient BLDC"),
            primary_image_url=primary_img,
            transparent_image_url=transparent_img,
            imagePath=primary_img,
            images=p.get("images") or [primary_img],
            motor_colors=m_colors,
            blade_colors=b_colors,
            default_motor_color=def_m,
            default_blade_color=def_b,
            color_combinations=combinations,
            optionDefinitions=p.get("optionDefinitions"),
            colors=p.get("colors"),
            variants=p.get("variants"),
            price=float(p.get("price") or p.get("base_price", 14999.0)),
            variants_count=variants_count,
            motor_finish_ids=p.get("motor_finish_ids", []),
            blade_finish_ids=p.get("blade_finish_ids", []),
            tag=p.get("tag") or ("Bestseller" if "BLDC" in code else "Smart AI"),
        )
        summaries.append(summary)

    return summaries


@router.get("/products/{product_id}", response_model=PublicProductDetail)
def get_product_details(product_id: str):
    """Retrieve full product detail with finishes, variants, and gallery media."""
    product = products_repo.find_by_id(product_id) or products_repo.find_by_code(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )

    p_id = product["product_id"]
    code = product.get("product_code") or product.get("fanCode") or p_id

    motor_finishes = finishes_repo.find_by_ids(product.get("motor_finish_ids", []))
    blade_finishes = finishes_repo.find_by_ids(product.get("blade_finish_ids", []))

    if not motor_finishes:
        all_motors = finishes_repo.find_all(finish_type="motor", is_active=True)
        motor_finishes = all_motors[:6]
    if not blade_finishes:
        all_blades = finishes_repo.find_all(finish_type="blade", is_active=True)
        blade_finishes = all_blades[:6]

    variants = variants_repo.find_by_product(p_id, only_active=True)
    media = media_repo.find_by_product(p_id)

    def_m = product.get("default_motor_color") or "Matt Grey"
    def_b = product.get("default_blade_color") or "Teak Wooden"
    primary_img = (
        product.get("primary_image_url") 
        or product.get("imagePath")
        or f"/api/users/combination-image?fan_code={code}&motor_color={def_m}&blade_color={def_b}"
    )

    return PublicProductDetail(
        product=product,
        motor_finishes=motor_finishes,
        blade_finishes=blade_finishes,
        variants=variants,
        media=media,
        primary_image_url=primary_img,
        price=float(product.get("price") or product.get("base_price", 14999.0)),
    )


@router.get("/products/{product_id}/variants", response_model=List[FanVariant])
def get_product_variants(product_id: str):
    """Retrieve approved active variants for a fan model."""
    product = products_repo.find_by_id(product_id) or products_repo.find_by_code(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )

    variants = variants_repo.find_by_product(product["product_id"], only_active=True)
    return [FanVariant(**v) for v in variants]


@router.post("/products/{product_id}/resolve-variant", response_model=ResolveVariantResponse)
def resolve_variant_combination(product_id: str, payload: ResolveVariantRequest):
    """Enforces finish matrix validation and checks if combination is an approved manufactured variant."""
    product = products_repo.find_by_id(product_id) or products_repo.find_by_code(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )

    p_id = product["product_id"]
    code = product.get("product_code") or product.get("fanCode") or p_id

    # 1. Check explicit variant registration
    variant = variants_repo.find_exact(p_id, payload.motor_finish_id, payload.blade_finish_id)
    if variant and variant.get("is_active", True):
        return ResolveVariantResponse(
            is_valid=True,
            message="Valid manufactured variant combination.",
            variant=variant,
        )

    # 2. Check if product allows these finishes
    allowed_motors = product.get("motor_finish_ids", [])
    allowed_blades = product.get("blade_finish_ids", [])
    if allowed_motors and payload.motor_finish_id not in allowed_motors:
        return ResolveVariantResponse(
            is_valid=False,
            message="This motor finish is not offered for this ceiling fan model.",
        )
    if allowed_blades and payload.blade_finish_id not in allowed_blades:
        return ResolveVariantResponse(
            is_valid=False,
            message="This blade finish is not offered for this ceiling fan model.",
        )

    m_finish = finishes_repo.find_by_id(payload.motor_finish_id)
    b_finish = finishes_repo.find_by_id(payload.blade_finish_id)
    m_name = m_finish.get("name", "Custom") if m_finish else payload.motor_finish_id
    b_name = b_finish.get("name", "Custom") if b_finish else payload.blade_finish_id

    synthetic_variant = {
        "variant_id": f"dyn-{payload.motor_finish_id}-{payload.blade_finish_id}",
        "product_id": p_id,
        "motor_finish_id": payload.motor_finish_id,
        "blade_finish_id": payload.blade_finish_id,
        "sku": f"{code}-{payload.motor_finish_id[:4]}-{payload.blade_finish_id[:4]}",
        "price_adjustment": 0.0,
        "is_active": True,
        "product_image_url": f"/api/users/combination-image?fan_code={code}&motor_color={m_name}&blade_color={b_name}",
        "transparent_image_url": f"/api/users/combination-image?fan_code={code}&motor_color={m_name}&blade_color={b_name}&transparent=true",
    }

    return ResolveVariantResponse(
        is_valid=True,
        message="Valid custom configured combination.",
        variant=synthetic_variant,
    )


@router.get("/finishes", response_model=List[Finish])
def get_active_finishes(
    finish_type: Optional[str] = Query(None, alias="type"),
):
    """Retrieve all active motor and blade swatches."""
    ftype = finish_type if isinstance(finish_type, str) and finish_type else None
    finishes = finishes_repo.find_all(finish_type=ftype, is_active=True)
    return [Finish(**f) for f in finishes]


@router.get("/combination-image")
def get_combination_image(
    fan_code: Optional[str] = Query(None, alias="product_code"),
    id: Optional[str] = None,
    motor_color: str = "Matt Grey",
    blade_color: str = "Teak Wooden",
    transparent: bool = False,
):
    """Returns the combination image for the requested fan model and colors."""
    code = fan_code or id
    if not code:
        raise HTTPException(status_code=400, detail="fan_code is required")

    prod = products_repo.find_by_code(code) or products_repo.find_by_id(code)
    actual_code = prod.get("product_code") or prod.get("fanCode") if prod else code

    m_slug = re.sub(r"[^a-z0-9]", "-", motor_color.lower())
    b_slug = re.sub(r"[^a-z0-9]", "-", blade_color.lower())

    comb_dir = UPLOADS_DIR / "fans" / actual_code / "combinations"
    comb_dir.mkdir(parents=True, exist_ok=True)

    target_name = f"{actual_code}_{m_slug}_{b_slug}{'_transparent' if transparent else ''}.png"
    target_file = comb_dir / target_name

    if target_file.exists() and target_file.stat().st_size > 500:
        return FileResponse(str(target_file), media_type="image/png")

    non_trans_file = comb_dir / f"{actual_code}_{m_slug}_{b_slug}.png"
    if non_trans_file.exists() and non_trans_file.stat().st_size > 500:
        if transparent:
            try:
                subprocess.run([
                    "convert", str(non_trans_file),
                    "-bordercolor", "white", "-border", "1x1",
                    "-fuzz", "12%", "-fill", "none", "-floodfill", "+0+0", "white",
                    "-shave", "1x1", str(target_file)
                ], check=True, timeout=5)
                if target_file.exists():
                    return FileResponse(str(target_file), media_type="image/png")
            except Exception:
                pass
        return FileResponse(str(non_trans_file), media_type="image/png")

    candidates = [
        UPLOADS_DIR / "fans" / actual_code / f"{actual_code}_hero_1_transparent.png",
        UPLOADS_DIR / "fans" / actual_code / f"{actual_code}_hero_1.png",
        UPLOADS_DIR / "fans" / actual_code / f"{actual_code}_primary.png",
        DATA_DIR / "products" / f"{actual_code}.png",
    ]

    for cand in candidates:
        if cand.exists() and cand.stat().st_size > 500:
            if transparent and "_transparent" not in cand.name:
                out_trans = comb_dir / f"{actual_code}_fallback_transparent.png"
                if out_trans.exists():
                    return FileResponse(str(out_trans), media_type="image/png")
                try:
                    subprocess.run([
                        "convert", str(cand),
                        "-bordercolor", "white", "-border", "1x1",
                        "-fuzz", "12%", "-fill", "none", "-floodfill", "+0+0", "white",
                        "-shave", "1x1", str(out_trans)
                    ], check=True, timeout=5)
                    if out_trans.exists():
                        return FileResponse(str(out_trans), media_type="image/png")
                except Exception:
                    pass
            return FileResponse(str(cand), media_type="image/png")

    raise HTTPException(status_code=404, detail="Combination image not found")


@router.get("/fan-cutout")
def get_fan_cutout(url: str):
    """On-demand transparent cutout endpoint."""
    clean = url.lstrip("/")
    abs_src = ROOT_DIR / clean
    data_src = DATA_DIR / clean

    actual_src = abs_src if abs_src.exists() else (data_src if data_src.exists() else None)
    if not actual_src or not actual_src.is_file():
        raise HTTPException(status_code=404, detail="Image file not found")

    trans_name = f"{actual_src.stem}_transparent.png"
    trans_path = actual_src.parent / trans_name

    if trans_path.exists() and trans_path.stat().st_size > 500:
        return FileResponse(str(trans_path), media_type="image/png")

    try:
        subprocess.run([
            "convert", str(actual_src),
            "-bordercolor", "white", "-border", "1x1",
            "-fuzz", "12%", "-fill", "none", "-floodfill", "+0+0", "white",
            "-shave", "1x1", str(trans_path)
        ], check=True, timeout=5)
        if trans_path.exists():
            return FileResponse(str(trans_path), media_type="image/png")
    except Exception:
        pass

    return FileResponse(str(actual_src), media_type="image/png")


# Backward compatibility aliases for test suites
get_user_products = get_products
get_user_finishes = get_active_finishes
get_user_product_variants = get_product_variants

