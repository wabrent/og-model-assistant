"""
API Router for health checks.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.database import get_db
from core.cache import cache

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns status of:
    - Database connection
    - Redis connection
    - OpenGradient service
    """
    health = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": False,
        "redis": False,
        "opengradient": False,
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health["status"] = "degraded"
    
    # Check Redis
    try:
        redis_ok = await cache.exists("_health_check")
        health["redis"] = redis_ok
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health["status"] = "degraded"
    
    # Check OpenGradient (basic check)
    try:
        from services.opengradient_service import og_service
        # Just check if service is initialized
        health["opengradient"] = og_service is not None
    except Exception as e:
        logger.error(f"OpenGradient health check failed: {e}")
        health["status"] = "degraded"
    
    # Determine overall status
    if not health["database"]:
        health["status"] = "unhealthy"
    
    return health


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check - is the service ready to accept traffic?"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """Liveness check - is the service alive?"""
    return {"status": "alive"}
