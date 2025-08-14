from __future__ import annotations

from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

# Import models to register tables in SQLModel metadata
from app.models import risk  # noqa: F401
from app.models import audit  # noqa: F401


settings = get_settings()

engine = create_async_engine(settings.database_url, future=True, echo=False, pool_pre_ping=True)

async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False, autocommit=False
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
