"""
Admin Authentication, User, and Audit Log Domain Models.
Adheres to Master Development Plan Section 3 & 14 & 16.
"""
import uuid
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Admin email address")
    password: str = Field(..., min_length=6, description="Admin secret password")


class AdminUserPublic(BaseModel):
    admin_id: str = Field(..., description="UUID of admin")
    email: str = Field(..., description="Admin email")
    role: Literal["admin"] = Field("admin", description="Role is always admin")
    name: Optional[str] = Field(None, description="Administrator display name")
    is_active: bool = True
    last_login: Optional[str] = None


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminUserPublic


class AdminUser(AdminUserPublic):
    password_hash: str
    created_at: str


class AuditLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str = Field(...)
    action: str = Field(..., description="Action e.g. CREATE_PRODUCT, DEACTIVATE_FINISH")
    target_entity: str = Field(..., description="Entity e.g. product, finish, variant")
    target_id: str = Field(..., description="UUID of modified entity")
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
