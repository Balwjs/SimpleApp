from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger


class KillSwitchExecutor:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute_full_halt(self) -> None:
        # TODO: integrate with DhanHQ API
        await self._cancel_all_orders()
        await self._close_all_positions()
        await self._block_new_orders()
        logger.warning("kill_switch_executed")

    async def _cancel_all_orders(self) -> None:
        logger.info("cancel_all_orders")

    async def _close_all_positions(self) -> None:
        logger.info("close_all_positions")

    async def _block_new_orders(self) -> None:
        logger.info("block_new_orders")
