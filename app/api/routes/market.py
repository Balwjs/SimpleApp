from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Request

from app.services.dhan_client import DhanClient

router = APIRouter(prefix="/market", tags=["market"]) 


@router.get("/ltp")
async def ltp(
    symbol: str = Query(..., description="Trading symbol or instrument identifier per Dhan docs"),
    exchange: Optional[str] = Query(None, description="Exchange code if required by endpoint"),
):
    # Adjust the path and params to match exact Dhan endpoint shape
    try:
        async with DhanClient() as client:
            data = await client.get_generic("/ltp", params={"symbol": symbol, "exchange": exchange} if exchange else {"symbol": symbol})
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Broker error: {e}")


@router.get("/depth")
async def depth(
    symbol: str = Query(...),
    exchange: Optional[str] = Query(None),
    levels: int = Query(5, ge=1, le=20),
):
    try:
        async with DhanClient() as client:
            params = {"symbol": symbol, "levels": levels}
            if exchange:
                params["exchange"] = exchange
            data = await client.get_generic("/depth", params=params)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Broker error: {e}")


@router.get("/proxy")
async def proxy(request: Request, path: str = Query(..., description="Path under /v2, e.g. market/quotes/ltp")):
    try:
        # forward all query params except 'path'
        params: Dict[str, Any] = dict(request.query_params)
        params.pop("path", None)
        async with DhanClient() as client:
            data = await client.get_generic(path, params=params)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Broker error: {e}")


@router.post("/proxy")
async def proxy_post(request: Request, path: str = Query(..., description="Path under /v2 for POST, e.g. market/quotes/ltp")):
    try:
        body = await request.json()
        async with DhanClient() as client:
            resp = await client._request("POST", path, json=body)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Broker error: {e}")
