from __future__ import annotations

from typing import Any, Dict, Optional
import time

import httpx

from app.core.config import get_settings
from app.core.logging import logger


class CircuitBreakerState:
    def __init__(self, failure_threshold: int = 5, reset_timeout_sec: int = 30) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout_sec = reset_timeout_sec
        self.failures = 0
        self.opened_at: Optional[float] = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if time.time() - self.opened_at >= self.reset_timeout_sec:
            # half-open
            return True
        return False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.time()


class DhanClient:
    _cb = CircuitBreakerState()

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        settings = get_settings()
        # Expect settings.dhan_base_url like 'https://api.dhan.co/v2/'
        self.base_url = (base_url or settings.dhan_base_url).rstrip("/")
        self.api_key = api_key or settings.dhan_api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", "access-token": self.api_key or ""},
            timeout=httpx.Timeout(5.0, connect=5.0, read=5.0, write=5.0),
            transport=httpx.AsyncHTTPTransport(retries=2),
        )

    async def __aenter__(self) -> "DhanClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if not DhanClient._cb.allow():
            raise httpx.HTTPError("Circuit open for Dhan API")
        try:
            response = await self._client.request(method, path.lstrip("/"), **kwargs)
            response.raise_for_status()
            DhanClient._cb.record_success()
            return response
        except httpx.HTTPStatusError as e:
            DhanClient._cb.record_failure()
            logger.error("dhan_http_status", status=e.response.status_code, body=e.response.text)
            raise
        except httpx.HTTPError as e:
            DhanClient._cb.record_failure()
            logger.error("dhan_http_error", error=str(e))
            raise

    async def get_generic(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        resp = await self._request("GET", path, params=params or {})
        return resp.json()

    # Example endpoints
    async def get_positions(self) -> list[dict[str, Any]]:
        resp = await self._request("GET", "positions")
        return resp.json()

    async def get_orders(self) -> list[dict[str, Any]]:
        resp = await self._request("GET", "orders")
        return resp.json()

    async def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self._request("POST", "orders", json=payload)
        return resp.json()

    async def cancel_all_orders(self) -> Dict[str, Any]:
        resp = await self._request("POST", "orders/cancel_all")
        return resp.json()

    async def get_funds(self) -> Dict[str, Any]:
        resp = await self._request("GET", "funds")
        return resp.json()

    async def get_holdings(self) -> list[Dict[str, Any]]:
        resp = await self._request("GET", "holdings")
        return resp.json()
