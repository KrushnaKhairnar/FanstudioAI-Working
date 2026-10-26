"""
Application configuration using Pydantic Settings.
"""
import os
from pathlib import Path
from typing import Optional, List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _parse_cors(value: Optional[str]) -> List[str]:
    defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    if not value:
        return defaults
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return parts or defaults


class Settings(BaseSettings):
    PROJECT_NAME: str = "FanStudioAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "fanstudio"
    DB_NAME: str = "fanstudio"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    UPLOAD_DIR: str = str(BACKEND_ROOT / "uploads")
    DATA_DIR: str = str(BACKEND_ROOT / "data")

    GEMINI_API_KEY: Optional[str] = None
    APP_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
settings.DB_NAME = settings.MONGODB_DB_NAME
if not settings.UPLOAD_DIR:
    settings.UPLOAD_DIR = str(BACKEND_ROOT / "uploads")
if not settings.DATA_DIR:
    settings.DATA_DIR = str(BACKEND_ROOT / "data")
# Allow CORS_ORIGINS from env as comma-separated string via os.environ override
_cors_env = os.getenv("CORS_ORIGINS")
if _cors_env:
    settings.CORS_ORIGINS = _parse_cors(_cors_env)
if settings.APP_URL and settings.APP_URL not in settings.CORS_ORIGINS:
    settings.CORS_ORIGINS.append(settings.APP_URL)
