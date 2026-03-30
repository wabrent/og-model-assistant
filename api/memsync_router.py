"""
API Router for MemSync (long-term memory) operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from loguru import logger

from services.memsync_service import memsync_service, get_memsync_service

router = APIRouter(prefix="/api/memsync", tags=["MemSync"])


class StoreMemoryRequest(BaseModel):
    messages: List[Dict[str, str]]
    agent_id: str = "og-assistant"
    thread_id: Optional[str] = None
    source: str = "chat"


class SearchMemoriesRequest(BaseModel):
    query: str
    limit: int = 5
    rerank: bool = True


class MemoryResponse(BaseModel):
    status: str
    memories: Optional[List[Dict[str, Any]]] = None
    user_bio: Optional[str] = None
    message: Optional[str] = None


@router.post("/memories", response_model=MemoryResponse)
async def store_memory(
    request: StoreMemoryRequest,
    service = Depends(get_memsync_service),
):
    """
    Store conversation to extract and save memories.
    """
    try:
        result = await service.store_memory(
            messages=request.messages,
            agent_id=request.agent_id,
            thread_id=request.thread_id,
            source=request.source,
        )
        return result
    except Exception as e:
        logger.error(f"Store memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memories/search", response_model=MemoryResponse)
async def search_memories(
    request: SearchMemoriesRequest,
    service = Depends(get_memsync_service),
):
    """
    Search for relevant memories using semantic search.
    """
    try:
        result = await service.search_memories(
            query=request.query,
            limit=request.limit,
            rerank=request.rerank,
        )
        return result
    except Exception as e:
        logger.error(f"Search memories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_profile(
    service = Depends(get_memsync_service),
):
    """
    Get user profile with bio and insights.
    """
    try:
        profile = await service.get_user_profile()
        return profile
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    service = Depends(get_memsync_service),
):
    """
    Delete a specific memory.
    """
    try:
        result = await service.delete_memory(memory_id)
        return result
    except Exception as e:
        logger.error(f"Delete memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
