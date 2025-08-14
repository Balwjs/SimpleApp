from __future__ import annotations

import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.session import async_session_maker
from app.models.risk import RiskSettings
from app.services.risk_service import RiskService
from app.services.kill_switch_executor import KillSwitchExecutor
from app.services.dhan_client import DhanClient, CircuitBreakerState


scheduler: Optional[AsyncIOScheduler] = None


async def poll_and_enforce_risk() -> None:
    try:
        async with async_session_maker() as session:  # type: AsyncSession
            risk_service = RiskService(session)
            settings = await risk_service.get_or_create_risk_settings()

            # TODO: replace with actual P&L computation via broker + DB positions
            total_pl = await compute_total_pnl(session)
            per_position_pl = await compute_per_position_pnl(session)

            # Enforce thresholds at 95%
            if total_pl <= -RiskService.trigger_level(settings.max_daily_total_loss):
                await risk_service.activate_kill_switch("max_daily_total_loss_reached")
                await KillSwitchExecutor(session).execute_full_halt()
            elif total_pl >= RiskService.trigger_level(settings.max_daily_total_profit_target):
                await risk_service.activate_kill_switch("max_daily_total_profit_target_reached")
                await KillSwitchExecutor(session).execute_full_halt()

            for symbol, pnl in per_position_pl.items():
                if pnl <= -RiskService.trigger_level(settings.max_daily_loss_per_position):
                    # TODO: close single position via broker
                    logger.warning("position_loss_limit", symbol=symbol, pnl=pnl)
                if pnl >= RiskService.trigger_level(settings.per_position_daily_profit_target):
                    # TODO: close single position via broker
                    logger.info("position_profit_target", symbol=symbol, pnl=pnl)
    except Exception as e:
        logger.error("risk_poll_error", error=str(e))


async def compute_total_pnl(session: AsyncSession) -> float:
    # TODO: implement from positions via DhanClient if needed
    return 0.0


async def compute_per_position_pnl(session: AsyncSession) -> dict[str, float]:
    # TODO: implement from positions via DhanClient if needed
    return {}


async def start_scheduler() -> None:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(poll_and_enforce_risk, "interval", seconds=2, id="risk_poll")
        scheduler.start()
        logger.info("scheduler_started")


async def shutdown_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("scheduler_stopped")
