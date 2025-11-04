from datetime import date
from typing import Dict
import httpx
from ..config import HYPERLIQUID_BASE


def _base_url() -> str:
    # Known public base; can be overridden by env
    return HYPERLIQUID_BASE or "https://api.hyperliquid.xyz"


async def fetch_wallet_activity(wallet: str, start: date, end: date) -> Dict:
    # This function attempts to gather trades, positions, funding, fees.
    # If certain endpoints are unavailable, it returns partial data; the PnL calculator handles missing pieces.
    base = _base_url()
    activity: Dict = {"trades": [], "positions": [], "funding": [], "fees": [], "closes": {}}

    async with httpx.AsyncClient(timeout=30) as client:
        # Placeholder endpoints; adjust if official docs differ.
        # Implementations should map to actual HyperLiquid APIs.
        try:
            # Example: per-user fills/trades
            r = await client.get(f"{base}/user/trades", params={"user": wallet, "start": start.isoformat(), "end": end.isoformat()})
            if r.status_code == 200:
                activity["trades"] = r.json()
        except Exception:
            pass

        try:
            # Example: funding payments per user per day
            r = await client.get(f"{base}/user/funding", params={"user": wallet, "start": start.isoformat(), "end": end.isoformat()})
            if r.status_code == 200:
                activity["funding"] = r.json()
        except Exception:
            pass

        try:
            # Example: fees per user
            r = await client.get(f"{base}/user/fees", params={"user": wallet, "start": start.isoformat(), "end": end.isoformat()})
            if r.status_code == 200:
                activity["fees"] = r.json()
        except Exception:
            pass

        try:
            # Daily close prices per symbol (for marking to market). If API not provided, leave empty.
            r = await client.get(f"{base}/market/daily_closes", params={"start": start.isoformat(), "end": end.isoformat()})
            if r.status_code == 200:
                activity["closes"] = r.json()
        except Exception:
            pass

    return activity


