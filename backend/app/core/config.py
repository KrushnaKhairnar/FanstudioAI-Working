"""
Application configuration using Pydantic Settings (with fallback for standalone environments).
"""
import os
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


# Load .env if present
env_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass


class Settings(BaseSettings):
    PROJECT_NAME: str = "FanStudioAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Server ports
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # MongoDB Configuration
    MONGODB_URI: Optional[str] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/fanstudioai")
    MONGODB_DB_NAME: Optional[str] = os.getenv("MONGODB_DB_NAME", "fanstudio")
    DB_NAME: str = os.getenv("MONGODB_DB_NAME", "fanstudio")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    APP_URL: Optional[str] = os.getenv("APP_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
if settings.MONGODB_DB_NAME:
    settings.DB_NAME = settings.MONGODB_DB_NAME
if settings.APP_URL and settings.APP_URL not in settings.CORS_ORIGINS:
    settings.CORS_ORIGINS.append(settings.APP_URL)
