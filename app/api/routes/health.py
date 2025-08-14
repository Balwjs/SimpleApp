from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
async def ready() -> dict:
    return {"status": "ready"}
