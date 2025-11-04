from typing import Tuple, Dict, Any
from ..config import MODEL_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL
import json
import math


async def get_insight(token: Dict[str, Any], market_chart: Dict[str, Any] | None, vs_currency: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    if MODEL_PROVIDER.lower() == "openai" and OPENAI_API_KEY:
        try:
            return await _openai_insight(token, market_chart, vs_currency)
        except Exception:
            pass
    return _mock_insight(token, market_chart, vs_currency), {"provider": "mock", "model": "heuristic-v1"}


def _mock_insight(token: Dict[str, Any], market_chart: Dict[str, Any] | None, vs_currency: str) -> Dict[str, Any]:
    md = token.get("market_data", {})
    pct_24h = md.get("price_change_percentage_24h")
    sentiment = "Neutral"
    if isinstance(pct_24h, (int, float)):
        if pct_24h > 2:
            sentiment = "Bullish"
        elif pct_24h < -2:
            sentiment = "Bearish"
    trend = "mixed"
    if market_chart and market_chart.get("prices"):
        prices = [p[1] for p in market_chart["prices"][-min(30, len(market_chart["prices"])):]]
        if len(prices) >= 3:
            if prices[-1] > prices[0] * 1.05:
                trend = "up"
            elif prices[-1] < prices[0] * 0.95:
                trend = "down"
            else:
                trend = "sideways"
    reasoning = f"24h change {pct_24h}% suggests {sentiment.lower()} bias; recent trend {trend}."
    return {"reasoning": reasoning, "sentiment": sentiment}


async def _openai_insight(token: Dict[str, Any], market_chart: Dict[str, Any] | None, vs_currency: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    import httpx
    system = "You are an analyst. Return JSON only. Keys: reasoning, sentiment (Bullish/Neutral/Bearish)."
    prompt = {
        "id": token.get("id"),
        "symbol": token.get("symbol"),
        "name": token.get("name"),
        "market_data": token.get("market_data", {}),
        "vs_currency": vs_currency,
        "has_history": bool(market_chart),
    }
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Analyze this token and respond JSON only: {json.dumps(prompt)}"},
    ]
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {"model": OPENAI_MODEL, "messages": messages, "response_format": {"type": "json_object"}}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed, {"provider": "openai", "model": OPENAI_MODEL}


