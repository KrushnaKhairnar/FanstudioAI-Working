"""
FanProduct Domain Model representing the ceiling fan catalog item.
Includes specifications, motor housing colors, blade colors, default finishes, and combinations.
"""
import uuid
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from app.models.specifications import FanSpecifications


class ColorCombinationItem(BaseModel):
    combination_id: str
    motor_color: str
    blade_color: str
    image_url: str
    transparent_image_url: Optional[str] = None
    price: Optional[float] = None


class FanProductBase(BaseModel):
    product_code: str = Field(..., min_length=2, max_length=100, description="Unique product catalog code e.g. FAN-0001 or AIREX_8_BLADES")
    name: str = Field(..., min_length=2, max_length=150, description="Product display name")
    fanName: Optional[str] = None
    fanCode: Optional[str] = None
    productId: Optional[str] = None
    description: Optional[str] = Field(None, max_length=2000, description="Marketing & technical description")
    status: Literal["draft", "active", "inactive"] = Field("active", description="Catalog lifecycle status")
    specifications: Optional[FanSpecifications] = None
    
    # Color combinations and finishes
    motor_colors: List[str] = Field(default_factory=list, description="Available motor housing colors")
    blade_colors: List[str] = Field(default_factory=list, description="Available blade colors & finishes")
    default_motor_color: Optional[str] = None
    default_blade_color: Optional[str] = None
    color_combinations: List[Dict[str, Any]] = Field(default_factory=list, description="Pre-mapped color finish combinations")
    
    blade_finish_ids: List[str] = Field(default_factory=list, description="Array of available blade finish IDs")
    motor_finish_ids: List[str] = Field(default_factory=list, description="Array of available motor finish IDs")
    
    primary_image_url: Optional[str] = None
    transparent_image_url: Optional[str] = None
    imagePath: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    
    optionDefinitions: Optional[Dict[str, List[str]]] = None
    colors: Optional[List[Dict[str, Any]]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    
    tag: Optional[str] = None
    base_price: float = 12990.0
    price: float = 12990.0


class FanProductCreate(FanProductBase):
    pass


class FanProductUpdate(BaseModel):
    product_code: Optional[str] = None
    name: Optional[str] = None
    fanName: Optional[str] = None
    fanCode: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["draft", "active", "inactive"]] = None
    specifications: Optional[FanSpecifications] = None
    motor_colors: Optional[List[str]] = None
    blade_colors: Optional[List[str]] = None
    default_motor_color: Optional[str] = None
    default_blade_color: Optional[str] = None
    blade_finish_ids: Optional[List[str]] = None
    motor_finish_ids: Optional[List[str]] = None
    primary_image_url: Optional[str] = None
    transparent_image_url: Optional[str] = None
    price: Optional[float] = None


class FanProduct(FanProductBase):
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Primary identifier for product")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
