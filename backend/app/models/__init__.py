"""
FanStudioAI Pydantic Domain Models Package.
"""
from backend.app.models.specifications import FanSpecifications, FORBIDDEN_SPEC_FIELDS
from backend.app.models.finish import Finish, FinishCreate, FinishUpdate
from backend.app.models.variant import FanVariant, FanVariantCreate, FanVariantUpdate
from backend.app.models.product import FanProduct, FanProductCreate, FanProductUpdate
from backend.app.models.media import ProductMedia, ProductMediaCreate, ProductMediaUpdate
from backend.app.models.ai import (
    AIProductConfiguration,
    AIJob,
    AIJobCreate,
    RoomAnalysis,
    GeneratedResult,
)
from backend.app.models.admin import (
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
