# Dapplooker Backend API

FastAPI backend providing token insights and HyperLiquid wallet PnL analysis.

## Features

- **Token Insight API**: CoinGecko data + AI-generated token analysis
- **HyperLiquid PnL API**: Daily PnL calculation (realized, unrealized, fees, funding)

## API Endpoints

- `POST /api/token/{id}/insight` - Get token data and AI-generated insight
- `GET /api/hyperliquid/{wallet}/pnl?start=YYYY-MM-DD&end=YYYY-MM-DD` - Get daily PnL for a wallet
- `GET /health` - Health check endpoint

## Setup Instructions

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ with pip

### Option 1: Docker Compose (Recommended)

1. **Clone the repository** (if not already done)

2. **Copy environment file**
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` file** (optional, defaults work for basic testing)
   ```bash
   MODEL_PROVIDER=mock
   OPENAI_API_KEY=your_key_here  # Only if using OpenAI
   OPENAI_MODEL=gpt-4o-mini
   COINGECKO_BASE=https://api.coingecko.com/api/v3
   ```

4. **Start the service**
   ```bash
   docker-compose up --build
   ```

   The service will be available at `http://localhost:8000`

5. **Access API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

6. **Stop the service**
   ```bash
   docker-compose down
   ```

### Option 2: Docker (Manual)

1. **Copy environment file**
   ```bash
   cp env.example .env
   ```

2. **Build the image**
   ```bash
   docker build -t dapplooker-backend .
   ```

3. **Run the container**
   ```bash
   docker run --rm -p 8000:8000 --env-file .env dapplooker-backend
   ```

### Option 3: Local Python Development

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env as needed
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Environment Variables

See `.env.example` for reference. Key variables:

- `MODEL_PROVIDER`: `mock` (default) or `openai`
- `OPENAI_API_KEY`: Required if `MODEL_PROVIDER=openai`
- `OPENAI_MODEL`: Model name, e.g., `gpt-4o-mini`
- `COINGECKO_BASE`: CoinGecko API base URL (default: `https://api.coingecko.com/api/v3`)
- `HYPERLIQUID_BASE`: HyperLiquid API base URL (optional, uses default if empty)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## API Usage Examples

### Token Insight

```bash
curl -X POST "http://localhost:8000/api/token/bitcoin/insight" \
  -H "Content-Type: application/json" \
  -d '{
    "vs_currency": "usd",
    "history_days": 30
  }'
```

### HyperLiquid PnL

```bash
curl "http://localhost:8000/api/hyperliquid/0x123.../pnl?start=2025-01-01&end=2025-01-31"
```

## Testing

Run the test suite:

```bash
# Using pytest
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

### Test Structure

- `tests/test_token_insight.py` - Token insight API tests
- `tests/test_pnl.py` - PnL computation tests
- `tests/test_hyperliquid.py` - HyperLiquid API tests

## Postman Collection

A Postman collection is included in `postman_collection.json`. Import it into Postman to test all endpoints easily.

### Import Instructions

1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json` file
4. All endpoints will be available with example requests

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── routers/
│   │   ├── token.py         # Token insight endpoints
│   │   └── hyperliquid.py   # HyperLiquid PnL endpoints
│   └── services/
│       ├── coingecko_client.py  # CoinGecko API client
│       ├── ai_provider.py       # AI insight provider (mock/OpenAI)
│       ├── hyperliquid_client.py # HyperLiquid API client
│       └── pnl.py               # PnL computation logic
├── tests/
│   ├── test_token_insight.py
│   ├── test_pnl.py
│   └── test_hyperliquid.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── env.example
├── postman_collection.json
└── README.md
```

## Notes

### AI Provider

- **Default (`mock`)**: No external API calls. Returns deterministic insights based on market data heuristics.
- **OpenAI**: Set `MODEL_PROVIDER=openai` and provide `OPENAI_API_KEY` in `.env` file.

⚠️ **Important**: Never commit `.env` files with API keys to version control.

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Code Quality

```bash
# Run linter (if configured)
pylint app/

# Format code (if configured)
black app/
```


