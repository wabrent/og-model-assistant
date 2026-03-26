"""
Chat service for AI conversations using OpenGradient LLM.
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from loguru import logger

from core.config import settings
from models.db_models import Model, ChatSession, UserQuery
from models.schemas import ChatRequest
from core.database import async_session_maker
from sqlalchemy import select


class ChatService:
    """Service for handling AI chat conversations."""
    
    def __init__(self):
        self._llm = None
        self._system_prompt = None
    
    @property
    def llm(self):
        """Lazy load OpenGradient LLM."""
        if self._llm is None:
            try:
                import opengradient as og
                self._llm = og.LLM(private_key=settings.private_key)

                # Ensure OPG approval (reduced from 10.0 to 1.0 for testing)
                try:
                    approval = self._llm.ensure_opg_approval(opg_amount=1.0)
                    logger.info(f"OPG Permit2 allowance: {approval.allowance_after}")
                except Exception as e:
                    logger.warning(f"Could not ensure OPG approval: {e}")

            except Exception as e:
                logger.error(f"Failed to initialize OpenGradient LLM: {e}")
                raise
        return self._llm
    
    def _build_system_prompt(self, models: List[Model]) -> str:
        """Build system prompt with model information."""
        models_text = self._format_models_for_prompt(models)
        
        return f"""You are a friendly assistant for the OpenGradient ecosystem.

You can help with:
- Finding AI models on the OpenGradient Model Hub
- Answering questions about OpenGradient, twin.fun, BitQuant
- General conversation and greetings

Format of model list: name|category|author|description

RULES:
1. Be friendly and conversational - respond to greetings, small talk naturally
2. Only search for models when user explicitly asks for them
3. Search by ALL fields - name, category, author and description
4. Suggest ONLY real models from the list
5. Give exact model names and explain why they fit
6. If nothing found - say so honestly
7. Answer in the same language the user writes in
8. NEVER mention how many models you searched through
9. After recommending models always add: "You can find these models on https://hub.opengradient.ai/models"
10. Always recommend AT LEAST 7 models when searching

You also know about these OpenGradient ecosystem products:

**twin.fun** (https://www.twin.fun/):
A marketplace for AI-powered digital twins - agents modeled after real people (crypto influencers, investors, builders). Each twin has a tradeable Key on a bonding curve. Holding keys unlocks access to chat with the twin, pitch ideas, debate, get feedback. Built onchain.

**BitQuant** (https://www.bitquant.io/):
An open-source AI agent framework by OpenGradient for building quantitative AI agents. Focuses on ML-powered analytics, trading strategies, portfolio management, and DeFi quant analysis.

**OpenGradient** (https://www.opengradient.ai/):
A decentralized AI infrastructure platform that uses blockchain for verifiable model inference. Provides open and verifiable AI onchain: model hosting, secure inference, and AI agent execution.

MODEL LIST:
{models_text}"""
    
    def _format_models_for_prompt(self, models: List[Model]) -> str:
        """Format models for system prompt."""
        lines = []
        for m in models:
            name = m.name or ""
            task = m.task_name or ""
            author = m.author_username or ""
            desc = (m.description or "")[:100].replace("\n", " ").strip()
            lines.append(f"{name}|{task}|{author}|{desc}")
        return "\n".join(lines)
    
    async def _get_system_prompt(self, db) -> str:
        """Get or build system prompt with current models."""
        # Get all active models
        result = await db.execute(
            select(Model).where(Model.is_active == True)
        )
        models = result.scalars().all()
        
        return self._build_system_prompt(models)
    
    async def chat(
        self,
        db,
        request: ChatRequest,
    ) -> Dict[str, Any]:
        """
        Process chat message and return response.
        """
        start_time = time.time()
        session_id = request.session_id or f"session_{int(time.time() * 1000)}"
        
        try:
            # Get or create chat session
            chat_session = await self._get_or_create_session(db, session_id, request.user_id)
            
            # Get system prompt
            system_prompt = await self._get_system_prompt(db)
            
            # Load or initialize conversation history
            if not chat_session.messages:
                chat_session.messages = [{"role": "system", "content": system_prompt}]
            
            # Add user message
            user_message = {"role": "user", "content": request.message}
            chat_session.messages.append(user_message)
            chat_session.message_count += 1
            
            # Call LLM
            response_content = await self._call_llm(chat_session.messages, request)
            
            # Add assistant response
            assistant_message = {"role": "assistant", "content": response_content}
            chat_session.messages.append(assistant_message)
            chat_session.message_count += 1
            chat_session.updated_at = datetime.utcnow()
            
            # Save session
            await db.commit()
            await db.refresh(chat_session)
            
            # Extract suggested models from response
            suggested_models = self._extract_model_names(response_content)
            
            # Log query
            await self._log_query(
                db,
                session_id,
                request.message,
                len(suggested_models),
                time.time() - start_time,
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return {
                "reply": response_content,
                "session_id": session_id,
                "models_suggested": suggested_models,
                "response_time_ms": response_time_ms,
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        request: ChatRequest,
    ) -> str:
        """Call OpenGradient LLM with retry logic."""
        import opengradient as og
        
        for attempt in range(3):
            try:
                # Call LLM directly (it handles async internally)
                response = self.llm.chat(
                    model=og.TEE_LLM.GROK_4_FAST,
                    messages=messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
                # Handle both sync and async responses
                if hasattr(response, '__await__'):
                    response = await response
                return response.chat_output["content"]
            except Exception as e:
                error_msg = str(e)
                if attempt < 2:
                    logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(2)
                else:
                    logger.error(f"LLM call failed after 3 attempts: {e}")
                    # Fallback response if API fails
                    return self._get_fallback_response(messages[-1]["content"])
    
    async def _get_or_create_session(
        self,
        db,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> ChatSession:
        """Get existing chat session or create new one."""
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                messages=[],
                message_count=0,
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        return session
    
    async def _log_query(
        self,
        db,
        session_id: str,
        query_text: str,
        results_count: int,
        response_time: float,
    ):
        """Log user query for analytics."""
        user_query = UserQuery(
            session_id=session_id,
            query_text=query_text,
            query_type="chat",
            results_count=results_count,
            response_time_ms=response_time * 1000,
        )
        db.add(user_query)
        await db.commit()
    
    def _extract_model_names(self, text: str) -> List[str]:
        """Extract model names from LLM response."""
        # Simple extraction - looks for model name patterns
        import re
        # Match patterns like model-name or model_name
        pattern = r'\b([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)\b'
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]  # Limit to 10 unique models
    
    async def get_session_history(
        self,
        db,
        session_id: str,
    ) -> Optional[ChatSession]:
        """Get chat session with full history."""
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        db,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ChatSession]:
        """Get all sessions for a user."""
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_session(self, db, session_id: str) -> bool:
        """Delete a chat session."""
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            await db.delete(session)
            await db.commit()
            return True
        return False


# Global service instance
chat_service = ChatService()
