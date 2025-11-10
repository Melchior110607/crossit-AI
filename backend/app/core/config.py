from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "CrossIt - E-commerce Cross-Listing Platform"
    
    # Database
    # Docker: Uses PostgreSQL (set via docker-compose.yml)
    # Local: Uses SQLite by default (can override with .env)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./crossit.db"  # Default for local development
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
        "https://joanna-edgier-emil.ngrok-free.dev"
    ]
    
    # Base URL for OAuth redirects (can be ngrok URL)
    BASE_REDIRECT_URL: str = os.getenv("BASE_REDIRECT_URL", "http://localhost:3000")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "crossit-products")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    class Config:
        case_sensitive = True


settings = Settings()

