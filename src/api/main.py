"""
FastAPI application for property valuation.

TODO: Future improvements:
- [ ] Add WebSocket support for real-time predictions
- [ ] Implement GraphQL endpoint
- [ ] Add request caching
- [ ] Implement circuit breaker pattern
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import joblib

from src.api.routers import predictions, health
from src.core.config import config
from src.core.logger import logger

MODEL: Optional[Dict[str, Any]] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Args:
        app: FastAPI application instance

    Yields:
        None: Control back to FastAPI after startup

    Note:
        Loads model on startup and ensures cleanup on shutdown.
    """
    global MODEL
    model_path = config.get_model_path()
    logger.info(f"Loading model from {model_path}")
    MODEL = joblib.load(model_path)
    logger.info("Model loaded successfully")

    yield

    logger.info("Shutting down application")


app = FastAPI(
    title="Property Friends API",
    description="Real estate valuation predictions for Chilean properties",
    version=config.MODEL_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(predictions.router, tags=["predictions"])


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint providing API information.

    Returns:
        Dict[str, str]: API information including name, version, and status
    """
    return {
        "name": "Property Friends API",
        "version": config.MODEL_VERSION,
        "status": "running",
    }
