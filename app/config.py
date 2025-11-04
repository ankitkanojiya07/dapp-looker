import os


MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "mock")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

COINGECKO_BASE = os.getenv("COINGECKO_BASE", "https://api.coingecko.com/api/v3")

# Placeholder; if empty, client will use known default if available
HYPERLIQUID_BASE = os.getenv("HYPERLIQUID_BASE", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


