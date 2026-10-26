"""
Central API Router Registry.
The ONLY place routers are registered in the application.
"""
from fastapi import APIRouter

from backend.app.api.routes.admin.products import router as admin_products_router
from backend.app.api.routes.admin.finishes import router as admin_finishes_router
from backend.app.api.routes.admin.variants import router as admin_variants_router
from backend.app.api.routes.admin.media import router as admin_media_router
from backend.app.api.routes.admin.system import router as admin_system_router

from backend.app.api.routes.users.catalog import router as user_catalog_router
from backend.app.api.routes.users.rooms import router as user_rooms_router, upload_room_file
from backend.app.api.routes.users.visualize import router as user_visualize_router

api_router = APIRouter()

# Admin Routes (/api/admin/...)
api_router.include_router(admin_products_router)
api_router.include_router(admin_finishes_router)
api_router.include_router(admin_variants_router)
api_router.include_router(admin_media_router)
api_router.include_router(admin_system_router)

# User Routes (/api/users/...)
api_router.include_router(user_catalog_router)
api_router.include_router(user_rooms_router)
api_router.include_router(user_visualize_router)

# Compatibility Alias for Room Upload
api_router.add_api_route(
    "/api/rooms/upload",
    upload_room_file,
    methods=["POST"],
    tags=["User Room Upload & Preprocessing"],
    status_code=201,
)

__all__ = ["api_router"]
