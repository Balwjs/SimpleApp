from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.dhan_client import DhanClient

router = APIRouter(prefix="/positions", tags=["positions"]) 


@router.get("")
async def list_positions():
    async with DhanClient() as client:
        try:
            data = await client.get_positions()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Broker error: {e}")
    # TODO: compute P&L with LTP; placeholder passthrough
    return data


@router.get("/margin")
async def available_margin():
    async with DhanClient() as client:
        try:
            data = await client.get_funds()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Broker error: {e}")
    return data
