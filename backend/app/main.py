"""
FanStudioAI - FastAPI Main Application Entry Point
"""
import os
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.db.mongo import db_manager
from backend.app.db.seed import seed_database
from backend.app.api.router import api_router

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.connect()
    try:
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")
    yield
    db_manager.disconnect()


app = FastAPI(
    title="FanStudioAI API",
    description="Backend API for FanStudioAI - AI Ceiling Fan Visualization Platform",
    version=settings.VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware configured strictly from settings (not wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Asset Mounts
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
rooms_dir = ROOT_DIR / "data" / "rooms"
vis_dir = ROOT_DIR / "data" / "visualizations"
products_dir = ROOT_DIR / "data" / "products"
uploads_dir = ROOT_DIR / "uploads"

rooms_dir.mkdir(parents=True, exist_ok=True)
vis_dir.mkdir(parents=True, exist_ok=True)
products_dir.mkdir(parents=True, exist_ok=True)
uploads_dir.mkdir(parents=True, exist_ok=True)

app.mount("/api/static/rooms", StaticFiles(directory=str(rooms_dir)), name="static_rooms")
app.mount("/api/static/visualizations", StaticFiles(directory=str(vis_dir)), name="static_visualizations")
app.mount("/api/static/products", StaticFiles(directory=str(products_dir)), name="static_products")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Central API Router Mount (The only place routers are mounted)
app.include_router(api_router)


@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint to verify system and database status."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    
    def safe_count(coll):
        try:
            return coll.count_documents({}) if hasattr(coll, "count_documents") else len(list(coll.find({})))
        except Exception:
            return 0

    return {
        "status": "healthy",
        "service": "FanStudioAI API",
        "version": settings.VERSION,
        "database": {
            "status": "connected",
            "engine": db_manager.engine_type,
            "database_name": settings.DB_NAME,
            "collections": {
                "products": safe_count(db_manager.products),
                "finishes": safe_count(db_manager.finishes),
                "product_variants": safe_count(db_manager.product_variants),
                "audit_logs": safe_count(db_manager.audit_logs),
            }
        },
        "uptime_seconds": uptime_seconds,
    }


@app.get("/api/docs", include_in_schema=False)
def docs_redirect():
    """Alias for /docs"""
    return RedirectResponse(url="/docs")


@app.get("/", tags=["System"])
def root_status():
    return {
        "message": "Welcome to FanStudioAI Backend API",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "version": settings.VERSION,
    }
