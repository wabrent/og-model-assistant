"""
Core configuration and settings for the application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenGradient
    private_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/og_assistant"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "og_assistant"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Bots
    telegram_bot_token: Optional[str] = None
    discord_bot_token: Optional[str] = None
    
    # Sync
    sync_interval_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
