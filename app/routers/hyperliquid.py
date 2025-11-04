from fastapi import APIRouter, HTTPException, Path, Query
from datetime import date
from typing import Dict
from ..services.hyperliquid_client import fetch_wallet_activity
from ..services.pnl import compute_daily_pnl


router = APIRouter()


@router.get("/{wallet}/pnl")
async def wallet_pnl(
    wallet: str = Path(..., description="Wallet address"),
    start: date = Query(..., description="Start date YYYY-MM-DD"),
    end: date = Query(..., description="End date YYYY-MM-DD"),
):
    if end < start:
        raise HTTPException(status_code=400, detail="end must be >= start")

    try:
        activity: Dict = await fetch_wallet_activity(wallet, start, end)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch HyperLiquid data: {e}")

    try:
        daily, summary = compute_daily_pnl(activity, start, end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PnL computation error: {e}")

    return {
        "wallet": wallet,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "daily": daily,
        "summary": summary,
        "diagnostics": {
            "data_source": "hyperliquid_api",
            "notes": "PnL calculated using daily close prices",
        },
    }


