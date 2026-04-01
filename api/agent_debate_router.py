"""
AI Agent Debate API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.agent_debate_service import agent_debate_service

router = APIRouter(prefix="/api/debate", tags=["Agent Debate"])


class DebateRequest(BaseModel):
    topic: str
    rounds: int = 3
    custom_topic: Optional[str] = None


@router.get("/topics")
async def get_topics():
    """Get available debate topics."""
    return {"topics": agent_debate_service.get_available_topics()}


@router.post("/run")
async def run_debate(request: DebateRequest):
    """Start a debate between two AI agents."""
    result = await agent_debate_service.run_debate(
        topic=request.topic,
        rounds=request.rounds,
        custom_topic=request.custom_topic
    )
    return result
