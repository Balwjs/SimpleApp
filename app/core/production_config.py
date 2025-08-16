"""
Production Configuration
Optimized settings for production deployment
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator

class ProductionSettings(BaseSettings):
    """Production-specific configuration settings"""
    
    # Environment
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    
    # Security
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./app.db"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    
    # CORS
    cors_origins: list = ["https://your-domain.com"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_allow_headers: list = ["Authorization", "Content-Type"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    log_file: str = "logs/app.log"
    log_max_size: int = 100 * 1024 * 1024  # 100MB
    log_backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    
    # Dhan Integration
    dhan_api_key: Optional[str] = None
    dhan_secret_key: Optional[str] = None
    dhan_base_url: str = "https://api.dhan.co"
    dhan_timeout: int = 30
    
    # Risk Management
    default_max_daily_loss: float = 500.0
    default_max_position_loss: float = 100.0
    default_profit_target: float = 200.0
    default_total_profit_target: float = 1000.0
    
    # Performance
    max_concurrent_requests: int = 1000
    request_timeout: int = 60
    enable_compression: bool = True
    enable_caching: bool = True
    
    # Backup
    backup_enabled: bool = True
    backup_interval: int = 24 * 60 * 60  # 24 hours
    backup_retention_days: int = 30
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "CHANGE_ME_IN_PRODUCTION":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        if "*" in v and cls.environment == "production":
            raise ValueError("Wildcard CORS not allowed in production")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Production settings instance
production_settings = ProductionSettings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    # Force production settings
    production_settings.environment = "production"
    production_settings.debug = False
    production_settings.log_level = "WARNING"
    
    # Security hardening
    production_settings.cors_origins = [
        os.getenv("ALLOWED_ORIGIN", "https://your-domain.com")
    ]
    
    # Database optimization
    production_settings.database_pool_size = int(os.getenv("DB_POOL_SIZE", "50"))
    production_settings.database_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "100"))
    
    # Performance tuning
    production_settings.workers = int(os.getenv("WORKERS", "8"))
    production_settings.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "2000"))
