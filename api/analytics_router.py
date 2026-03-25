"""
API Router for analytics operations.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from core.database import get_db
from services.analytics_service import analytics_service
from services.model_service import model_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/stats")
async def get_global_stats(db: AsyncSession = Depends(get_db)):
    """
    Get global statistics including:
    - Total models
    - Total queries
    - Unique users
    - Average response time
    - Top tasks and authors
    """
    try:
        stats = await analytics_service.get_global_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/top")
async def get_top_queries(
    period: str = Query(default="7d", pattern="^(\\d+[hdw]|30d)$"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get most popular queries.
    
    - **period**: Time period (e.g., 1h, 7d, 30d)
    - **limit**: Number of results (1-100)
    """
    try:
        queries = await analytics_service.get_top_queries(db, period, limit)
        return {
            "queries": queries,
            "period": period,
            "total": len(queries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/popular")
async def get_popular_models(
    period: str = Query(default="7d", pattern="^(\\d+[hdw]|30d)$"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get most popular models by selections.
    
    - **period**: Time period (e.g., 1h, 7d, 30d)
    - **limit**: Number of results (1-100)
    """
    try:
        models = await analytics_service.get_popular_models(db, period, limit)
        return {
            "models": models,
            "period": period,
            "total": len(models),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/stats")
async def get_query_stats(
    period: str = Query(default="7d", pattern="^(\\d+[hdw]|30d)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get query statistics for a period.
    
    Returns:
    - Total queries
    - Queries by type
    - Average response time
    - Daily query counts
    """
    try:
        stats = await analytics_service.get_query_stats(db, period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/stats")
async def get_model_stats(db: AsyncSession = Depends(get_db)):
    """
    Get model statistics including:
    - Total and active models
    - Models by task category
    - Top authors by model count
    """
    try:
        stats = await model_service.get_model_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
