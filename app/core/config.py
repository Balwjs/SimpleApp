from __future__ import annotations

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
    secret: str = "CHANGE_ME"

    # Dhan HQ
    dhan_base_url: str = "https://sandbox.dhan.co/v2/"
    dhan_api_key: str | None = None
    dhan_client_id: str | None = None
    dhan_client_secret: str | None = None

    # RMS defaults
    max_daily_total_loss: float = 1200.0
    max_daily_loss_per_position: float = 200.0
    per_position_daily_profit_target: float = 500.0
    max_daily_total_profit_target: float = 2200.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
