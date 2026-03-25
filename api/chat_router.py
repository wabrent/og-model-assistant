"""
API Router for chat operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.database import get_db
from models.schemas import ChatRequest, ChatResponse
from services.chat_service import chat_service
from services.analytics_service import analytics_service
from services.token_service import token_service, PRICING

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and get AI response.
    Free to use - tokens auto-claimed every 5 hours.
    """
    try:
        user_id = request.session_id
        
        # Get user (no deduction - free usage)
        user = await token_service.get_or_create_user(db, user_id)
        
        # Process chat
        result = await chat_service.chat(db, request)

        return {
            "reply": result["reply"],
            "session_id": result["session_id"],
            "models_suggested": result["models_suggested"],
            "response_time_ms": result["response_time_ms"],
            "token_balance": user.balance,
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full chat history for a session."""
    try:
        session = await chat_service.get_session_history(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_user_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get all chat sessions for a user."""
    try:
        sessions = await chat_service.get_user_sessions(db, user_id, limit, offset)
        return {
            "sessions": [s.to_dict() for s in sessions],
            "total": len(sessions),
        }
    except Exception as e:
        logger.error(f"Get user sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session."""
    try:
        deleted = await chat_service.delete_session(db, session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
