from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


client = TestClient(app)


@patch("app.routers.hyperliquid.fetch_wallet_activity")
@patch("app.routers.hyperliquid.compute_daily_pnl")
def test_wallet_pnl_success(mock_compute_pnl, mock_fetch_activity):
    """Test successful wallet PnL retrieval"""
    # Mock activity data
    mock_activity = {
        "trades": [
            {"date": "2025-01-01T10:00:00Z", "symbol": "BTC", "side": "buy", "qty": 1, "price": 50000, "fee": 10}
        ],
        "funding": [],
        "fees": [],
        "closes": {"2025-01-01": {"BTC": 50000}}
    }
    
    # Mock daily PnL data
    mock_daily = [
        {
            "date": "2025-01-01",
            "realized_pnl_usd": 0.0,
            "unrealized_pnl_usd": 0.0,
            "fees_usd": 10.0,
            "funding_usd": 0.0,
            "net_pnl_usd": -10.0,
            "equity_usd": 9990.0
        }
    ]
    
    mock_summary = {
        "total_realized_usd": 0.0,
        "total_unrealized_usd": 0.0,
        "total_fees_usd": 10.0,
        "total_funding_usd": 0.0,
        "net_pnl_usd": -10.0
    }
    
    async def async_fetch_activity(*args, **kwargs):
        return mock_activity
    
    mock_fetch_activity.side_effect = async_fetch_activity
    mock_compute_pnl.return_value = (mock_daily, mock_summary)
    
    response = client.get(
        "/api/hyperliquid/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/pnl?start=2025-01-01&end=2025-01-01"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["wallet"] == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    assert data["start"] == "2025-01-01"
    assert data["end"] == "2025-01-01"
    assert len(data["daily"]) == 1
    assert "summary" in data
    assert "diagnostics" in data


def test_wallet_pnl_invalid_date_range():
    """Test wallet PnL with invalid date range (end < start)"""
    response = client.get(
        "/api/hyperliquid/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/pnl?start=2025-01-31&end=2025-01-01"
    )
    
    assert response.status_code == 400
    assert "end must be >= start" in response.json()["detail"]


@patch("app.routers.hyperliquid.fetch_wallet_activity")
def test_wallet_pnl_fetch_error(mock_fetch_activity):
    """Test wallet PnL when fetching activity fails"""
    async def async_fetch_activity_error(*args, **kwargs):
        raise Exception("API error")
    
    mock_fetch_activity.side_effect = async_fetch_activity_error
    
    response = client.get(
        "/api/hyperliquid/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/pnl?start=2025-01-01&end=2025-01-31"
    )
    
    assert response.status_code == 502
    assert "Failed to fetch HyperLiquid data" in response.json()["detail"]


@patch("app.routers.hyperliquid.fetch_wallet_activity")
@patch("app.routers.hyperliquid.compute_daily_pnl")
def test_wallet_pnl_computation_error(mock_compute_pnl, mock_fetch_activity):
    """Test wallet PnL when computation fails"""
    async def async_fetch_activity(*args, **kwargs):
        return {"trades": [], "funding": [], "fees": [], "closes": {}}
    
    mock_fetch_activity.side_effect = async_fetch_activity
    mock_compute_pnl.side_effect = Exception("Computation error")
    
    response = client.get(
        "/api/hyperliquid/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/pnl?start=2025-01-01&end=2025-01-31"
    )
    
    assert response.status_code == 500
    assert "PnL computation error" in response.json()["detail"]


def test_wallet_pnl_multi_day():
    """Test wallet PnL for multiple days"""
    with patch("app.routers.hyperliquid.fetch_wallet_activity") as mock_fetch_activity, \
         patch("app.routers.hyperliquid.compute_daily_pnl") as mock_compute_pnl:
        
        mock_activity = {
            "trades": [],
            "funding": [],
            "fees": [],
            "closes": {}
        }
        
        mock_daily = [
            {"date": "2025-01-01", "realized_pnl_usd": 100.0, "unrealized_pnl_usd": 0.0, "fees_usd": 5.0, "funding_usd": 0.0, "net_pnl_usd": 95.0, "equity_usd": 10095.0},
            {"date": "2025-01-02", "realized_pnl_usd": 50.0, "unrealized_pnl_usd": 0.0, "fees_usd": 3.0, "funding_usd": 0.0, "net_pnl_usd": 47.0, "equity_usd": 10142.0}
        ]
        
        mock_summary = {
            "total_realized_usd": 150.0,
            "total_unrealized_usd": 0.0,
            "total_fees_usd": 8.0,
            "total_funding_usd": 0.0,
            "net_pnl_usd": 142.0
        }
        
        async def async_fetch_activity(*args, **kwargs):
            return mock_activity
        
        mock_fetch_activity.side_effect = async_fetch_activity
        mock_compute_pnl.return_value = (mock_daily, mock_summary)
        
        response = client.get(
            "/api/hyperliquid/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb/pnl?start=2025-01-01&end=2025-01-02"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["daily"]) == 2
        assert data["summary"]["net_pnl_usd"] == 142.0

