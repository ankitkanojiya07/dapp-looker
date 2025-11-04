from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import Optional
from ..services.coingecko_client import fetch_token, fetch_market_chart
from ..services.ai_provider import get_insight


class TokenInsightRequest(BaseModel):
    vs_currency: Optional[str] = "usd"
    history_days: Optional[int] = 30


router = APIRouter()


@router.post("/{id}/insight")
async def token_insight(
    id: str = Path(..., description="CoinGecko token id, e.g., 'chainlink'"),
    body: TokenInsightRequest = TokenInsightRequest(),
):
    try:
        token = await fetch_token(id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch token: {e}")

    market_chart = None
    if body.history_days and body.history_days > 0:
        try:
            market_chart = await fetch_market_chart(id, body.vs_currency, body.history_days)
        except Exception:
            market_chart = None

    insight, model_info = await get_insight(token, market_chart, body.vs_currency)

    market_data = token.get("market_data", {})
    current_price = market_data.get("current_price", {}).get("usd" if body.vs_currency == "usd" else body.vs_currency)

    response = {
        "source": "coingecko",
        "token": {
            "id": token.get("id"),
            "symbol": token.get("symbol"),
            "name": token.get("name"),
            "market_data": {
                "current_price_usd": current_price if body.vs_currency == "usd" else token.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap_usd": token.get("market_data", {}).get("market_cap", {}).get("usd"),
                "total_volume_usd": token.get("market_data", {}).get("total_volume", {}).get("usd"),
                "price_change_percentage_24h": token.get("market_data", {}).get("price_change_percentage_24h")
            }
        },
        "insight": insight,
        "model": model_info
    }

    return response


