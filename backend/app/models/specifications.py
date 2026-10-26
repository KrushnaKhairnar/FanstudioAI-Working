"""
FanSpecifications Domain Model.
Strictly adheres to Master Development Plan Section 5:
Only category, blade_type, blade_count, motor_type are allowed.
Explicitly forbids: Default Sweep, Customizable Sweep, Voltage, Air Delivery, CFM.
"""
from typing import Set
from pydantic import BaseModel, Field, model_validator


FORBIDDEN_SPEC_FIELDS: Set[str] = {
    "default_sweep",
    "customizable_sweep",
    "voltage",
    "air_delivery",
    "cfm",
}


class FanSpecifications(BaseModel):
    category: str = Field(..., min_length=1, max_length=100, description="Fan style category e.g. Modern Luxury, Scandinavian")
    blade_type: str = Field(..., min_length=1, max_length=100, description="Blade material and construction type")
    blade_count: int = Field(..., ge=1, le=10, description="Number of blades")
    motor_type: str = Field(..., min_length=1, max_length=100, description="Motor type e.g. Precision Inverter DC Motor")

    model_config = {
        "extra": "forbid",  # Rejects any unapproved fields including forbidden fields
        "json_schema_extra": {
            "example": {
                "category": "Modern Luxury",
                "blade_type": "Aerodynamic Sculpted Composite",
                "blade_count": 3,
                "motor_type": "Precision Inverter DC Motor",
            }
        }
    }

    @model_validator(mode="before")
    @classmethod
    def check_forbidden_fields(cls, data: dict):
        if isinstance(data, dict):
            found_forbidden = [k for k in data.keys() if k.lower() in FORBIDDEN_SPEC_FIELDS]
            if found_forbidden:
                raise ValueError(
                    f"Forbidden specification fields detected: {found_forbidden}. "
                    "Default Sweep, Customizable Sweep, Voltage, Air Delivery, and CFM are strictly prohibited."
                )
        return data
