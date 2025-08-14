from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from nicegui import ui

from app.core.config import get_settings
from app.core.logging import configure_logging, logger
from app.db.session import init_db
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.api.routes.health import router as health_router
from app.api.routes.risk import router as risk_router
from app.api.routes.kill_switch import router as kill_router
from app.api.routes.positions import router as positions_router
from app.api.routes.orders import router as orders_router
from app.api.routes.market import router as market_router
from app.ui.dashboard import create_ui


settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup:begin", environment=settings.environment)
    await init_db()
    await start_scheduler()
    yield
    logger.info("shutdown:begin")
    await shutdown_scheduler()


app = FastAPI(title="Trading Middleware", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API
app.include_router(health_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(kill_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(market_router, prefix="/api")

# Metrics
@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


# NiceGUI
create_ui()
ui.run_with(app, mount_path="/")
