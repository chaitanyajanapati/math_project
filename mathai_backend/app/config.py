"""Application configuration using Pydantic Settings for environment-driven config."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    Environment variables can be set with APP_ prefix, e.g.:
    - APP_API_BASE=http://0.0.0.0:8000
    - APP_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    """
    
    # API Configuration
    api_base: str = "http://127.0.0.1:8000"
    api_title: str = "MathAI Backend"
    api_version: str = "1.0.0"
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Alternative dev port
    ]
    cors_allow_credentials: bool = True
    
    # Data Storage
    data_dir: Path = Path("data")
    
    # Model Path Configuration
    model_path: Path = Path(__file__).resolve().parents[2] / "mathai_ai_models"
    
    # Feature Flags
    enable_progressive_hints: bool = True
    enable_solution_explainer: bool = True
    enable_metrics: bool = True
    enable_rate_limiting: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Performance
    enable_cache: bool = True
    cache_size: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Global settings instance
settings = Settings()
