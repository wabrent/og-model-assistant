"""
API Router for sync operations.
"""
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.database import get_db
from models.schemas import SyncStatusResponse, SyncTriggerResponse
from services.opengradient_service import og_service
from services.model_service import model_service

router = APIRouter(prefix="/api/sync", tags=["Sync"])

# Sync state
_sync_state = {
    "is_syncing": False,
    "last_sync_at": None,
    "next_sync_at": None,
    "last_sync_stats": None,
}


async def run_sync(db: AsyncSession):
    """Run model sync in background."""
    global _sync_state
    
    if _sync_state["is_syncing"]:
        logger.warning("Sync already in progress")
        return
    
    _sync_state["is_syncing"] = True
    logger.info("Starting model sync...")
    
    try:
        stats = await og_service.sync_models()
        _sync_state["last_sync_at"] = datetime.utcnow()
        _sync_state["last_sync_stats"] = stats
        logger.info(f"Sync completed: {stats}")
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        _sync_state["last_sync_stats"] = {"error": str(e)}
    finally:
        _sync_state["is_syncing"] = False


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(db: AsyncSession = Depends(get_db)):
    """Get current sync status."""
    try:
        stats = await model_service.get_model_stats(db)
        
        return {
            "is_syncing": _sync_state["is_syncing"],
            "last_sync_at": _sync_state["last_sync_at"],
            "next_sync_at": _sync_state["next_sync_at"],
            "models_count": stats.get("active_models", 0),
            "status": "syncing" if _sync_state["is_syncing"] else "idle",
        }
    except Exception as e:
        logger.error(f"Get sync status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger", response_model=SyncTriggerResponse)
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual model sync."""
    global _sync_state
    
    if _sync_state["is_syncing"]:
        return {
            "status": "already_syncing",
            "message": "Sync is already in progress",
        }
    
    background_tasks.add_task(run_sync, db)
    
    return {
        "status": "started",
        "message": "Sync started in background",
    }


@router.get("/history")
async def get_sync_history():
    """Get sync history (last sync stats)."""
    return {
        "last_sync_at": _sync_state["last_sync_at"],
        "last_sync_stats": _sync_state["last_sync_stats"],
    }
