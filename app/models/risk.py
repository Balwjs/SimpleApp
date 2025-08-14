from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import TimeStampedModel


class RiskSettings(TimeStampedModel, table=True):
    __tablename__ = "risk_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)

    max_daily_total_loss: float
    max_daily_loss_per_position: float
    per_position_daily_profit_target: float
    max_daily_total_profit_target: float

    risk_locked: bool = False
    risk_lock_until: Optional[datetime] = None


class KillSwitchStatus(TimeStampedModel, table=True):
    __tablename__ = "kill_switch_status"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)
    is_active: bool = False
    reason: Optional[str] = None


class KillSwitchEvent(TimeStampedModel, table=True):
    __tablename__ = "kill_switch_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)
    action: str
    reason: str
