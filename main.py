"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from loguru import logger
import os

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
from api.model_status_router import router as model_status_router


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


# Create FastAPI app
app = FastAPI(
    title="OpenGradient Model Assistant",
    description="AI-powered assistant for OpenGradient Model Hub with smart search, chat, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
app.include_router(model_status_router)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Disable reload for Python 3.13 compatibility
    )
