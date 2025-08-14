from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditService:
    def __init__(self, session: AsyncSession, user_id: Optional[str] = None) -> None:
        self.session = session
        self.user_id = user_id

    async def record(self, event: str, *, detail: Optional[str] = None, path: Optional[str] = None, success: bool = True) -> None:
        self.session.add(
            AuditLog(user_id=self.user_id, event=event, detail=detail, path=path, success=success)
        )
        await self.session.commit()
