from datetime import date
from app.services.pnl import compute_daily_pnl


def test_pnl_computation_simple():
    """Test basic PnL computation with buy and sell"""
    activity = {
        "trades": [
            {"date": "2025-08-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 1, "price": 100, "fee": 1},
            {"date": "2025-08-02T10:00:00Z", "symbol": "BTC", "side": "sell", "qty": 1, "price": 110, "fee": 1},
        ],
        "funding": [
            {"date": "2025-08-02T12:00:00Z", "symbol": "BTC", "amount_usd": -0.5}
        ],
        "fees": [],
        "closes": {
            "2025-08-01": {"BTC": 100},
            "2025-08-02": {"BTC": 110},
        },
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 8, 1), date(2025, 8, 2))
    assert len(daily) == 2
    assert summary["total_realized_usd"] > 0
    # Buy: -1 fee, Sell: (110-100)*1 - 1 fee = 9, total realized = 9
    assert daily[0]["realized_pnl_usd"] == -1.0  # Buy trade with fee
    assert daily[1]["realized_pnl_usd"] == 9.0  # Sell trade: (110-100)*1 - 1 fee = 9


def test_pnl_computation_unrealized():
    """Test PnL computation with unrealized gains"""
    activity = {
        "trades": [
            {"date": "2025-01-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 1, "price": 100, "fee": 1},
        ],
        "funding": [],
        "fees": [],
        "closes": {
            "2025-01-01": {"BTC": 100},
            "2025-01-02": {"BTC": 120},
        },
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 2))
    assert len(daily) == 2
    assert daily[0]["unrealized_pnl_usd"] == 0.0  # Price same as buy
    assert daily[1]["unrealized_pnl_usd"] == 20.0  # Price increased by 20
    assert summary["total_unrealized_usd"] == 20.0


def test_pnl_computation_multiple_symbols():
    """Test PnL computation with multiple symbols"""
    activity = {
        "trades": [
            {"date": "2025-01-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 1, "price": 100, "fee": 1},
            {"date": "2025-01-01T11:00:00Z", "symbol": "ETH", "side": "buy", "qty": 2, "price": 50, "fee": 0.5},
        ],
        "funding": [],
        "fees": [],
        "closes": {
            "2025-01-01": {"BTC": 100, "ETH": 50},
            "2025-01-02": {"BTC": 110, "ETH": 45},
        },
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 2))
    assert len(daily) == 2
    # BTC: (110-100)*1 = 10, ETH: (45-50)*2 = -10, net unrealized = 0
    assert daily[1]["unrealized_pnl_usd"] == 0.0  # Net unrealized


def test_pnl_computation_funding():
    """Test PnL computation with funding payments"""
    activity = {
        "trades": [],
        "funding": [
            {"date": "2025-01-01T12:00:00Z", "symbol": "BTC", "amount_usd": 5.0},
            {"date": "2025-01-02T12:00:00Z", "symbol": "BTC", "amount_usd": -2.0},
        ],
        "fees": [],
        "closes": {},
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 2))
    assert len(daily) == 2
    assert daily[0]["funding_usd"] == 5.0
    assert daily[1]["funding_usd"] == -2.0
    assert summary["total_funding_usd"] == 3.0


def test_pnl_computation_fees():
    """Test PnL computation with fees"""
    activity = {
        "trades": [],
        "funding": [],
        "fees": [
            {"date": "2025-01-01T12:00:00Z", "amount_usd": 10.0},
            {"date": "2025-01-02T12:00:00Z", "amount_usd": 5.0},
        ],
        "closes": {},
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 2))
    assert len(daily) == 2
    assert daily[0]["fees_usd"] == 10.0
    assert daily[1]["fees_usd"] == 5.0
    assert summary["total_fees_usd"] == 15.0


def test_pnl_computation_partial_sell():
    """Test PnL computation with partial position closure"""
    activity = {
        "trades": [
            {"date": "2025-01-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 2, "price": 100, "fee": 1},
            {"date": "2025-01-02T10:00:00Z", "symbol": "BTC", "side": "sell", "qty": 1, "price": 110, "fee": 1},
        ],
        "funding": [],
        "fees": [],
        "closes": {
            "2025-01-01": {"BTC": 100},
            "2025-01-02": {"BTC": 110},
        },
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 2))
    assert len(daily) == 2
    assert daily[1]["realized_pnl_usd"] == 9.0  # (110-100)*1 - 1 fee = 9
    assert daily[1]["unrealized_pnl_usd"] == 10.0  # Remaining 1 BTC at 110 vs avg 100 = 10


def test_pnl_computation_empty_activity():
    """Test PnL computation with no activity"""
    activity = {
        "trades": [],
        "funding": [],
        "fees": [],
        "closes": {},
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 3))
    assert len(daily) == 3
    assert all(d["realized_pnl_usd"] == 0.0 for d in daily)
    assert all(d["unrealized_pnl_usd"] == 0.0 for d in daily)
    assert summary["net_pnl_usd"] == 0.0


def test_pnl_computation_single_day():
    """Test PnL computation for a single day"""
    activity = {
        "trades": [
            {"date": "2025-01-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 1, "price": 100, "fee": 1},
        ],
        "funding": [
            {"date": "2025-01-01T12:00:00Z", "symbol": "BTC", "amount_usd": 2.0}
        ],
        "fees": [
            {"date": "2025-01-01T14:00:00Z", "amount_usd": 0.5}
        ],
        "closes": {
            "2025-01-01": {"BTC": 105},
        },
    }
    daily, summary = compute_daily_pnl(activity, date(2025, 1, 1), date(2025, 1, 1))
    assert len(daily) == 1
    assert daily[0]["realized_pnl_usd"] == -1.0  # Buy trade fee
    assert daily[0]["unrealized_pnl_usd"] == 5.0  # (105-100)*1
    assert daily[0]["funding_usd"] == 2.0
    assert daily[0]["fees_usd"] == 1.5  # 1 from trade + 0.5 from fees
    assert daily[0]["net_pnl_usd"] == 4.5  # -1 + 5 - 1.5 + 2 = 4.5


