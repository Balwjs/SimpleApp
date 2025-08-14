from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.dhan_client import DhanClient

router = APIRouter(prefix="/orders", tags=["orders"]) 


@router.get("")
async def list_orders():
    async with DhanClient() as client:
        try:
            data = await client.get_orders()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Broker error: {e}")
    return data


@router.post("")
async def place_order(payload: dict):
    async with DhanClient() as client:
        try:
            data = await client.place_order(payload)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Broker error: {e}")
    return data


@router.post("/cancel_all")
async def cancel_all():
    async with DhanClient() as client:
        try:
            data = await client.cancel_all_orders()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Broker error: {e}")
    return data
