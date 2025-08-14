from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.risk_service import RiskService
from app.services.kill_switch_executor import KillSwitchExecutor


router = APIRouter(prefix="/kill", tags=["kill-switch"]) 


class ActionPayload(BaseModel):
    reason: str


@router.get("/status")
async def status(session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    status = await service.get_kill_switch_status()
    return status


@router.post("/activate")
async def activate(payload: ActionPayload, session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    status = await service.activate_kill_switch(payload.reason)
    await KillSwitchExecutor(session).execute_full_halt()
    return status


@router.post("/deactivate")
async def deactivate(payload: ActionPayload, session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    status = await service.deactivate_kill_switch(payload.reason)
    return status
