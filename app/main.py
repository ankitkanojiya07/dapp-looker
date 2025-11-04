from fastapi import FastAPI
from .routers.token import router as token_router
from .routers.hyperliquid import router as hyperliquid_router


app = FastAPI(title="Dapplooker Backend", version="1.0.0")

app.include_router(token_router, prefix="/api/token", tags=["token"])
app.include_router(hyperliquid_router, prefix="/api/hyperliquid", tags=["hyperliquid"])


@app.get("/health")
def health():
    return {"status": "ok"}


