"""
FanStudioAI Pydantic Domain Models Package.
"""
from app.models.specifications import FanSpecifications, FORBIDDEN_SPEC_FIELDS
from app.models.finish import Finish, FinishCreate, FinishUpdate
from app.models.variant import FanVariant, FanVariantCreate, FanVariantUpdate
from app.models.product import FanProduct, FanProductCreate, FanProductUpdate
from app.models.media import ProductMedia, ProductMediaCreate, ProductMediaUpdate
from app.models.ai import (
    AIProductConfiguration,
    AIJob,
    AIJobCreate,
    RoomAnalysis,
    GeneratedResult,
)
from app.models.admin import (
    AdminUser,
    AdminUserPublic,
    AdminLoginRequest,
    AdminTokenResponse,
    AuditLog,
)

__all__ = [
    "FanSpecifications",
    "FORBIDDEN_SPEC_FIELDS",
    "Finish",
    "FinishCreate",
    "FinishUpdate",
    "FanVariant",
    "FanVariantCreate",
    "FanVariantUpdate",
    "FanProduct",
    "FanProductCreate",
    "FanProductUpdate",
    "ProductMedia",
    "ProductMediaCreate",
    "ProductMediaUpdate",
    "AIProductConfiguration",
    "AIJob",
    "AIJobCreate",
    "RoomAnalysis",
    "GeneratedResult",
    "AdminUser",
    "AdminUserPublic",
    "AdminLoginRequest",
    "AdminTokenResponse",
    "AuditLog",
]
