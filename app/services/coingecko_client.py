import httpx
from ..config import COINGECKO_BASE


async def fetch_token(token_id: str) -> dict:
    url = f"{COINGECKO_BASE}/coins/{token_id}"
    params = {"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def fetch_market_chart(token_id: str, vs_currency: str, days: int) -> dict:
    url = f"{COINGECKO_BASE}/coins/{token_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


