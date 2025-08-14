from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.risk_service import RiskService


router = APIRouter(prefix="/risk", tags=["risk"]) 


class RiskUpdate(BaseModel):
    max_daily_total_loss: Optional[float] = Field(default=None, ge=0)
    max_daily_loss_per_position: Optional[float] = Field(default=None, ge=0)
    per_position_daily_profit_target: Optional[float] = Field(default=None, ge=0)
    max_daily_total_profit_target: Optional[float] = Field(default=None, ge=0)


@router.get("/settings")
async def get_settings(session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    settings = await service.get_or_create_risk_settings()
    return settings


@router.post("/settings")
async def update_settings(payload: RiskUpdate, session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    try:
        updated = await service.update_thresholds(**{k: v for k, v in payload.dict().items() if v is not None})
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return updated


@router.post("/lock")
async def lock_settings(session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    settings = await service.lock_risk_until_next_day_5pm()
    return settings


@router.post("/unlock")
async def unlock_if_expired(session: AsyncSession = Depends(get_session)):
    service = RiskService(session)
    settings = await service.unlock_risk_if_expired()
    return settings
