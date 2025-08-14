from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.models.risk import RiskSettings, KillSwitchStatus, KillSwitchEvent


class RiskService:
    def __init__(self, session: AsyncSession, user_id: Optional[str] = None) -> None:
        self.session = session
        self.user_id = user_id
        self.settings = get_settings()

    async def get_or_create_risk_settings(self) -> RiskSettings:
        stmt = select(RiskSettings).where(RiskSettings.user_id == self.user_id)
        result = await self.session.execute(stmt)
        settings = result.scalar_one_or_none()
        if settings is None:
            settings = RiskSettings(
                user_id=self.user_id,
                max_daily_total_loss=self.settings.max_daily_total_loss,
                max_daily_loss_per_position=self.settings.max_daily_loss_per_position,
                per_position_daily_profit_target=self.settings.per_position_daily_profit_target,
                max_daily_total_profit_target=self.settings.max_daily_total_profit_target,
            )
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)
        return settings

    async def lock_risk_until_next_day_5pm(self) -> RiskSettings:
        settings = await self.get_or_create_risk_settings()
        if settings.risk_locked:
            return settings
        now = datetime.now()
        next_day = now + timedelta(days=1)
        lock_dt = datetime.combine(next_day.date(), time(17, 0))
        settings.risk_locked = True
        settings.risk_lock_until = lock_dt
        settings.touch()
        self.session.add(settings)
        await self.session.commit()
        return settings

    async def unlock_risk_if_expired(self) -> RiskSettings:
        settings = await self.get_or_create_risk_settings()
        if settings.risk_locked and settings.risk_lock_until and datetime.now() >= settings.risk_lock_until:
            settings.risk_locked = False
            settings.risk_lock_until = None
            settings.touch()
            self.session.add(settings)
            await self.session.commit()
        return settings

    async def update_thresholds(self, **kwargs) -> RiskSettings:
        settings = await self.get_or_create_risk_settings()
        await self.unlock_risk_if_expired()
        if settings.risk_locked:
            raise PermissionError("Risk settings are locked")
        for key, value in kwargs.items():
            if hasattr(settings, key) and isinstance(value, (int, float)):
                setattr(settings, key, float(value))
        settings.touch()
        self.session.add(settings)
        await self.session.commit()
        return settings

    @staticmethod
    def trigger_level(value: float) -> float:
        return value * 0.95

    async def get_kill_switch_status(self) -> KillSwitchStatus:
        stmt = select(KillSwitchStatus).where(KillSwitchStatus.user_id == self.user_id)
        result = await self.session.execute(stmt)
        status = result.scalar_one_or_none()
        if status is None:
            status = KillSwitchStatus(user_id=self.user_id, is_active=False)
            self.session.add(status)
            await self.session.commit()
            await self.session.refresh(status)
        return status

    async def activate_kill_switch(self, reason: str) -> KillSwitchStatus:
        status = await self.get_kill_switch_status()
        if status.is_active:
            return status
        status.is_active = True
        status.reason = reason
        status.touch()
        self.session.add(status)
        self.session.add(KillSwitchEvent(user_id=self.user_id, action="activate", reason=reason))
        await self.session.commit()
        logger.warning("kill_switch_activated", user_id=self.user_id, reason=reason)
        return status

    async def deactivate_kill_switch(self, reason: str) -> KillSwitchStatus:
        status = await self.get_kill_switch_status()
        status.is_active = False
        status.reason = reason
        status.touch()
        self.session.add(status)
        self.session.add(KillSwitchEvent(user_id=self.user_id, action="deactivate", reason=reason))
        await self.session.commit()
        logger.info("kill_switch_deactivated", user_id=self.user_id, reason=reason)
        return status
