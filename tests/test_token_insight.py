from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


client = TestClient(app)


def test_health():
    """Test health check endpoint"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@patch("app.routers.token.fetch_token")
@patch("app.routers.token.get_insight")
@patch("app.routers.token.fetch_market_chart")
def test_token_insight_success(mock_market_chart, mock_get_insight, mock_fetch_token):
    """Test successful token insight retrieval"""
    # Mock token data
    mock_token = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "market_data": {
            "current_price": {"usd": 50000},
            "market_cap": {"usd": 1000000000},
            "total_volume": {"usd": 50000000},
            "price_change_percentage_24h": 2.5
        }
    }
    
    mock_market_data = {
        "prices": [[1000, 45000], [2000, 50000]]
    }
    
    mock_insight = {
        "reasoning": "Test reasoning",
        "sentiment": "Bullish"
    }
    
    mock_model_info = {"provider": "mock", "model": "heuristic-v1"}
    
    # Create async mock functions
    async def async_fetch_token(*args, **kwargs):
        return mock_token
    
    async def async_fetch_market_chart(*args, **kwargs):
        return mock_market_data
    
    async def async_get_insight(*args, **kwargs):
        return (mock_insight, mock_model_info)
    
    mock_fetch_token.side_effect = async_fetch_token
    mock_market_chart.side_effect = async_fetch_market_chart
    mock_get_insight.side_effect = async_get_insight
    
    response = client.post(
        "/api/token/bitcoin/insight",
        json={"vs_currency": "usd", "history_days": 30}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "coingecko"
    assert data["token"]["id"] == "bitcoin"
    assert data["token"]["symbol"] == "btc"
    assert data["insight"]["sentiment"] == "Bullish"
    assert data["model"]["provider"] == "mock"
    assert "market_data" in data["token"]


@patch("app.routers.token.fetch_token")
def test_token_insight_invalid_token(mock_fetch_token):
    """Test token insight with invalid token ID"""
    async def async_fetch_token_error(*args, **kwargs):
        raise Exception("Token not found")
    
    mock_fetch_token.side_effect = async_fetch_token_error
    
    response = client.post(
        "/api/token/invalid-token/insight",
        json={"vs_currency": "usd", "history_days": 30}
    )
    
    assert response.status_code == 502
    assert "Failed to fetch token" in response.json()["detail"]


def test_token_insight_default_params():
    """Test token insight with default parameters"""
    with patch("app.routers.token.fetch_token") as mock_fetch_token, \
         patch("app.routers.token.get_insight") as mock_get_insight, \
         patch("app.routers.token.fetch_market_chart") as mock_market_chart:
        
        mock_token = {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "market_data": {
                "current_price": {"usd": 3000},
                "market_cap": {"usd": 500000000},
                "total_volume": {"usd": 20000000},
                "price_change_percentage_24h": -1.5
            }
        }
        
        mock_insight = {"reasoning": "Test", "sentiment": "Neutral"}
        mock_model_info = {"provider": "mock", "model": "heuristic-v1"}
        
        async def async_fetch_token(*args, **kwargs):
            return mock_token
        
        async def async_get_insight(*args, **kwargs):
            return (mock_insight, mock_model_info)
        
        async def async_fetch_market_chart(*args, **kwargs):
            return None
        
        mock_fetch_token.side_effect = async_fetch_token
        mock_get_insight.side_effect = async_get_insight
        mock_market_chart.side_effect = async_fetch_market_chart
        
        response = client.post(
            "/api/token/ethereum/insight",
            json={}
        )
        
        assert response.status_code == 200
        assert response.json()["token"]["id"] == "ethereum"


def test_token_insight_custom_currency():
    """Test token insight with custom currency"""
    with patch("app.routers.token.fetch_token") as mock_fetch_token, \
         patch("app.routers.token.get_insight") as mock_get_insight, \
         patch("app.routers.token.fetch_market_chart") as mock_market_chart:
        
        mock_token = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "market_data": {
                "current_price": {"usd": 50000, "eur": 45000},
                "market_cap": {"usd": 1000000000},
                "total_volume": {"usd": 50000000},
                "price_change_percentage_24h": 2.5
            }
        }
        
        mock_insight = {"reasoning": "Test", "sentiment": "Bullish"}
        mock_model_info = {"provider": "mock", "model": "heuristic-v1"}
        
        async def async_fetch_token(*args, **kwargs):
            return mock_token
        
        async def async_get_insight(*args, **kwargs):
            return (mock_insight, mock_model_info)
        
        async def async_fetch_market_chart(*args, **kwargs):
            return None
        
        mock_fetch_token.side_effect = async_fetch_token
        mock_get_insight.side_effect = async_get_insight
        mock_market_chart.side_effect = async_fetch_market_chart
        
        response = client.post(
            "/api/token/bitcoin/insight",
            json={"vs_currency": "eur", "history_days": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["token"]["market_data"]["current_price_usd"] == 50000


