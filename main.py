"""
Main FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core.config import settings
from core.database import init_db, close_db
from core.cache import cache
from core.logging_config import setup_logging

from api.models_router import router as models_router
from api.chat_router import router as chat_router
from api.analytics_router import router as analytics_router
from api.sync_router import router as sync_router
from api.health_router import router as health_router
from api.tokens_router import router as tokens_router
from api.user_stats_router import router as user_stats_router
from api.defi_router import router as defi_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting OpenGradient Model Assistant...")

    # Setup logging
    setup_logging()

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Connect to Redis
    await cache.connect()

    # Create static directory if not exists
    os.makedirs("static", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Auto-sync models on startup (for cloud deployments)
    try:
        from api.sync_router import run_sync
        from core.database import async_session_maker
        
        logger.info("🔄 Starting initial model sync...")
        async with async_session_maker() as db:
            await run_sync(db)
        logger.info("✅ Initial model sync completed!")
    except Exception as e:
        logger.error(f"⚠️ Initial sync failed: {e}. Use /api/sync/trigger to sync manually.")

    logger.info(f"Server starting on http://{settings.api_host}:{settings.api_port}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await cache.close()
    await close_db()
    logger.info("Shutdown complete")

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Create FastAPI app
app = FastAPI(
    title="OpenGradient Model Assistant",
    description="AI-powered assistant for OpenGradient Model Hub with smart search, chat, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(models_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(sync_router)
app.include_router(health_router)
app.include_router(tokens_router)
app.include_router(user_stats_router)
app.include_router(defi_router)


# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint - serves the main UI."""
    if os.path.exists("static/index.html"):
        return FileResponse(
            "static/index.html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {
        "message": "OpenGradient Model Assistant API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/developer")
async def developer_hub():
    """Developer Hub page."""
    if os.path.exists("static/developer.html"):
        return FileResponse("static/developer.html")
    return {"error": "Developer Hub not found"}


@app.get("/marketplace")
async def marketplace():
    """AI Marketplace page (coming soon)."""
    return {"message": "Marketplace - Coming Soon"}


@app.get("/academy")
async def academy():
    """AI Academy page (coming soon)."""
    return {"message": "Academy - Coming Soon"}


@app.get("/defi")
async def defi():
    """DeFi Hub page."""
    if os.path.exists("static/defi.html"):
        return FileResponse(
            "static/defi.html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "DeFi Hub - Coming Soon"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Disable reload for Python 3.13 compatibility
    )
