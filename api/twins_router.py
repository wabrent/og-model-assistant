"""
API Router for Digital Twins (twin.fun) operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from services.twins_service import twins_service, get_twins_service

router = APIRouter(prefix="/api/twins", tags=["Digital Twins"])


@router.get("")
async def get_twins(
    limit: int = 20,
    service = Depends(get_twins_service),
):
    """
    Get all digital twins with market data.
    """
    try:
        twins = await service.get_twins(limit)
        return {"twins": twins, "total": len(twins)}
    except Exception as e:
        logger.error(f"Get twins error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}")
async def get_twin(
    twin_id: str,
    service = Depends(get_twins_service),
):
    """
    Get a specific twin by ID.
    """
    try:
        twin = await service.get_twin(twin_id)
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        return twin
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get twin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}/trades")
async def get_twin_trades(
    twin_id: str,
    limit: int = 25,
    service = Depends(get_twins_service),
):
    """
    Get recent trades for a twin.
    """
    try:
        trades = await service.get_twin_trades(twin_id, limit)
        return {"trades": trades, "total": len(trades)}
    except Exception as e:
        logger.error(f"Get twin trades error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/holders/top")
async def get_top_holders(
    limit: int = 20,
    service = Depends(get_twins_service),
):
    """
    Get top holders across all twins.
    """
    try:
        holders = await service.get_top_holders(limit)
        return {"holders": holders, "total": len(holders)}
    except Exception as e:
        logger.error(f"Get top holders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/protocol")
async def get_protocol_stats(
    service = Depends(get_twins_service),
):
    """
    Get protocol-wide statistics.
    """
    try:
        stats = await service.get_protocol_stats()
        return stats
    except Exception as e:
        logger.error(f"Get protocol stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
