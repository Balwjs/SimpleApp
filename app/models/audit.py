from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user_id: Optional[str] = Field(default=None, index=True)
    event: str = Field(nullable=False)
    detail: Optional[str] = None
    path: Optional[str] = None
    success: bool = True
