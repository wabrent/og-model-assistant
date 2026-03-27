"""
API Router for model status monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from loguru import logger

from core.database import get_db
from services.model_status_service import model_status_service
from services.opengradient_service import og_service

router = APIRouter(prefix="/api/models", tags=["Model Status"])


@router.get("/status")
async def get_all_statuses(db: AsyncSession = Depends(get_db)):
    """Get status summary for all models."""
    try:
        summary = await model_status_service.get_status_summary(db)
        return summary
    except Exception as e:
        # Return default response on any error
        logger.error(f"Status endpoint failed: {e}")
        return {
            "total_models": 0,
            "online": 0,
            "offline": 0,
            "avg_response_time_ms": 0,
            "avg_uptime_percentage": 0,
        }


@router.get("/online")
async def get_online_models(db: AsyncSession = Depends(get_db)):
    """Get list of online models."""
    try:
        online = await model_status_service.get_online_models(db)
        return {"online_models": online, "total": len(online)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}")
async def get_model_status(
    model_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get current status of a specific model."""
    try:
        status = await model_status_service.get_model_status(db, model_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Model status not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def check_all_models_status(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger background check of all models status.
    Returns immediately, check runs in background.
    """
    try:
        # Start background task
        background_tasks.add_task(_run_status_check, db)
        
        return {
            "status": "started",
            "message": "Model status check started in background",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_status_check(db: AsyncSession):
    """Background task to check all models status."""
    try:
        result = await model_status_service.check_all_models(db)
        logger.info(f"Background status check complete: {result}")
    except Exception as e:
        logger.error(f"Background status check failed: {e}")


@router.post("/{model_id}/check")
async def check_single_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Check status of a specific model."""
    try:
        from models.db_models import Model
        from sqlalchemy import select
        
        result = await db.execute(
            select(Model).where(Model.id == model_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        status = await model_status_service.check_model_status(db, model)
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
