from datetime import date, timedelta
from typing import Dict, List, Tuple


def compute_daily_pnl(activity: Dict, start: date, end: date) -> Tuple[List[Dict], Dict]:
    # Inputs:
    # - activity.trades: list of {date, symbol, side, qty, price, realized?, fee?}
    # - activity.funding: list of {date, symbol, amount_usd}
    # - activity.fees: list of {date, amount_usd}
    # - activity.closes: mapping {date: {symbol: close_price}}
    # Output: (daily list, summary dict)

    days: List[date] = []
    d = start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)

    # Positions by symbol for unrealized PnL: {symbol: {qty, avg_price}}
    positions: Dict[str, Dict[str, float]] = {}

    def apply_trade(trade: Dict) -> float:
        symbol = trade.get("symbol")
        side = trade.get("side")  # "buy" or "sell"
        qty = float(trade.get("qty", 0))
        price = float(trade.get("price", 0))
        fee = float(trade.get("fee", 0))
        realized = 0.0
        pos = positions.get(symbol, {"qty": 0.0, "avg": 0.0})
        if side == "buy":
            new_qty = pos["qty"] + qty
            if new_qty > 0:
                pos["avg"] = (pos["avg"] * pos["qty"] + price * qty) / new_qty if (pos["qty"] + qty) != 0 else price
            pos["qty"] = new_qty
        else:  # sell
            close_qty = min(qty, pos["qty"]) if pos["qty"] > 0 else 0.0
            realized += (price - pos["avg"]) * close_qty
            pos["qty"] = max(0.0, pos["qty"] - close_qty)
        positions[symbol] = pos
        return realized - fee

    def unrealized_for_day(closes_for_day: Dict[str, float]) -> float:
        total = 0.0
        for symbol, pos in positions.items():
            qty = pos["qty"]
            if qty == 0:
                continue
            close = closes_for_day.get(symbol)
            if close is None:
                continue
            total += (close - pos["avg"]) * qty
        return total

    # Index activity by day
    by_day_trades: Dict[str, List[Dict]] = {}
    for t in activity.get("trades", []):
        day = (t.get("date") or "")[:10]
        by_day_trades.setdefault(day, []).append(t)

    by_day_funding: Dict[str, List[Dict]] = {}
    for f in activity.get("funding", []):
        day = (f.get("date") or "")[:10]
        by_day_funding.setdefault(day, []).append(f)

    by_day_fees: Dict[str, List[Dict]] = {}
    for f in activity.get("fees", []):
        day = (f.get("date") or "")[:10]
        by_day_fees.setdefault(day, []).append(f)

    closes_map: Dict[str, Dict[str, float]] = activity.get("closes", {})

    daily: List[Dict] = []
    equity = 10000.0  # Starting equity baseline (no DB). In practice, seed from API or parameter.
    total_realized = total_unrealized = total_fees = total_funding = 0.0

    for day in days:
        day_str = day.isoformat()
        realized = 0.0
        fees_usd = 0.0
        funding_usd = 0.0

        for t in by_day_trades.get(day_str, []):
            realized += apply_trade(t)

        for f in by_day_fees.get(day_str, []):
            fees_usd += float(f.get("amount_usd", f.get("fee", 0.0)))

        for f in by_day_funding.get(day_str, []):
            funding_usd += float(f.get("amount_usd", 0.0))

        unrealized = unrealized_for_day(closes_map.get(day_str, {}))

        net = realized + unrealized - fees_usd + funding_usd
        equity += net

        daily.append(
            {
                "date": day_str,
                "realized_pnl_usd": round(realized, 4),
                "unrealized_pnl_usd": round(unrealized, 4),
                "fees_usd": round(fees_usd, 4),
                "funding_usd": round(funding_usd, 4),
                "net_pnl_usd": round(net, 4),
                "equity_usd": round(equity, 4),
            }
        )

        total_realized += realized
        total_unrealized += unrealized
        total_fees += fees_usd
        total_funding += funding_usd

    summary = {
        "total_realized_usd": round(total_realized, 4),
        "total_unrealized_usd": round(total_unrealized, 4),
        "total_fees_usd": round(total_fees, 4),
        "total_funding_usd": round(total_funding, 4),
        "net_pnl_usd": round(total_realized + total_unrealized - total_fees + total_funding, 4),
    }

    return daily, summary


