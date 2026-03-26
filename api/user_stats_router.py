"""
API Router for user stats and achievements.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from core.database import get_db
from services.user_stats_service import (
    user_stats_service,
    achievement_service,
)

router = APIRouter(prefix="/api/user", tags=["User"])


@router.get("/stats")
async def get_user_stats(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user statistics and progress."""
    try:
        stats = await user_stats_service.get_stats(db, user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements")
async def get_user_achievements(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all user achievements."""
    try:
        achievements = await user_stats_service.get_user_achievements(db, user_id)
        all_achievements = await achievement_service.get_all_achievements()
        
        # Mark unlocked achievements
        unlocked_ids = {a["achievement_id"] for a in achievements}
        for achievement in all_achievements:
            achievement["unlocked"] = achievement["achievement_id"] in unlocked_ids
            if achievement["unlocked"]:
                # Find the unlocked achievement data
                unlocked_data = next(
                    (a for a in achievements if a["achievement_id"] == achievement["achievement_id"]),
                    None
                )
                achievement["unlocked_at"] = unlocked_data["unlocked_at"] if unlocked_data else None
        
        return {
            "achievements": all_achievements,
            "total_unlocked": len(achievements),
            "total_achievements": len(all_achievements),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get top users by experience."""
    try:
        leaderboard = await user_stats_service.get_leaderboard(db, limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-achievements")
async def get_all_achievements():
    """Get all available achievements."""
    try:
        achievements = await achievement_service.get_all_achievements()
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-achievements")
async def check_achievements(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check and unlock new achievements for user."""
    try:
        stats = await user_stats_service.get_or_create_stats(db, user_id)
        unlocked = await achievement_service.check_and_unlock(db, user_id, stats)
        
        return {
            "unlocked": unlocked,
            "total_unlocked": len(unlocked),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
