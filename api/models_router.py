"""
API Router for model operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger

from core.database import get_db
from models.schemas import (
    ModelSearchRequest, ModelSearchResponse, ModelResponse,
    ModelAnalyticsResponse
)
from services.model_service import model_service
from services.analytics_service import analytics_service

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.post("/search", response_model=ModelSearchResponse)
async def search_models(
    search_request: ModelSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search models with filters and full-text search.
    
    - **query**: Free text search across name, description, task, author
    - **task_name**: Filter by task category
    - **author_username**: Filter by author
    - **tags**: Filter by tags
    - **sort_by**: Sort by relevance, name, created_at, or popularity
    - **limit**: Number of results (1-100)
    - **offset**: Pagination offset
    """
    try:
        models, total = await model_service.search_models(db, search_request)
        
        return {
            "models": [m.to_dict() for m in models],
            "total": total,
            "limit": search_request.limit,
            "offset": search_request.offset,
            "has_more": (search_request.offset + search_request.limit) < total,
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[ModelResponse])
async def get_all_models(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get all models with pagination."""
    try:
        models, total = await model_service.get_all_models(db, limit, offset)
        return [m.to_dict() for m in models]
    except Exception as e:
        logger.error(f"Get models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific model by ID."""
    try:
        model = await model_service.get_model_by_id(db, model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Increment view count
        await model_service.increment_view(db, model_id)
        
        return model.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/name/{name}", response_model=ModelResponse)
async def get_model_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific model by name."""
    try:
        model = await model_service.get_model_by_name(db, name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        await model_service.increment_view(db, model.id)
        
        return model.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model by name error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    """Get all unique task categories."""
    try:
        tasks = await model_service.get_unique_tasks(db)
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/authors")
async def get_authors(db: AsyncSession = Depends(get_db)):
    """Get all unique authors."""
    try:
        authors = await model_service.get_unique_authors(db)
        return {"authors": authors}
    except Exception as e:
        logger.error(f"Get authors error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)):
    """Get all unique tags."""
    try:
        tags = await model_service.get_all_tags(db)
        return {"tags": tags}
    except Exception as e:
        logger.error(f"Get tags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/analytics", response_model=ModelAnalyticsResponse)
async def get_model_analytics(
    model_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific model."""
    try:
        analytics = await analytics_service.get_model_analytics(db, model_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Model analytics not found")
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
