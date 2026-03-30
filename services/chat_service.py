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


TEE_LLM_MODELS = {
    "grok-4-fast": {"provider": "x-ai", "description": "Fast reasoning and coding"},
    "grok-4": {"provider": "x-ai", "description": "Advanced reasoning"},
    "grok-4.1-fast": {"provider": "x-ai", "description": "Latest fast model"},
    "gpt-5": {"provider": "openai", "description": "Latest OpenAI model"},
    "gpt-4.1": {"provider": "openai", "description": "OpenAI GPT-4.1"},
    "o4-mini": {"provider": "openai", "description": "OpenAI o4-mini"},
    "claude-opus-4-6": {"provider": "anthropic", "description": "Claude Opus 4.6"},
    "claude-sonnet-4-6": {"provider": "anthropic", "description": "Claude Sonnet 4.6"},
    "claude-haiku-4-5": {"provider": "anthropic", "description": "Claude Haiku 4.5"},
    "gemini-2.5-pro": {"provider": "google", "description": "Gemini 2.5 Pro"},
    "gemini-2.5-flash": {"provider": "google", "description": "Gemini 2.5 Flash"},
    "gemini-3-pro": {"provider": "google", "description": "Gemini 3 Pro"},
}


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

                try:
                    approval = self._llm.ensure_opg_approval(opg_amount=5.0)
                    logger.info(f"OPG Permit2 allowance: {approval.allowance_after}")
                except Exception as e:
                    logger.warning(f"Could not ensure OPG approval: {e}")

            except Exception as e:
                logger.error(f"Failed to initialize OpenGradient LLM: {e}")
                raise
        return self._llm
    
    def _get_model_enum(self, model_name: str):
        """Get the TEE_LLM enum from model name."""
        import opengradient as og
        
        model_map = {
            "grok-4-fast": og.TEE_LLM.GROK_4_FAST,
            "grok-4": og.TEE_LLM.GROK_4,
            "grok-4.1-fast": og.TEE_LLM.GROK_4_1_FAST,
            "gpt-5": og.TEE_LLM.GPT_5,
            "gpt-4.1": og.TEE_LLM.GPT_4_1_2025_04_14,
            "o4-mini": og.TEE_LLM.O4_MINI,
            "claude-opus-4-6": og.TEE_LLM.CLAUDE_OPUS_4_6,
            "claude-opus-4-5": og.TEE_LLM.CLAUDE_OPUS_4_5,
            "claude-sonnet-4-6": og.TEE_LLM.CLAUDE_SONNET_4_6,
            "claude-sonnet-4-5": og.TEE_LLM.CLAUDE_SONNET_4_5,
            "claude-haiku-4-5": og.TEE_LLM.CLAUDE_HAIKU_4_5,
            "gemini-2.5-pro": og.TEE_LLM.GEMINI_2_5_PRO,
            "gemini-2.5-flash": og.TEE_LLM.GEMINI_2_5_FLASH,
            "gemini-2.5-flash-lite": og.TEE_LLM.GEMINI_2_5_FLASH_LITE,
            "gemini-3-pro": og.TEE_LLM.GEMINI_3_PRO,
            "gemini-3-flash": og.TEE_LLM.GEMINI_3_FLASH,
        }
        
        return model_map.get(model_name.lower(), og.TEE_LLM.GROK_4_FAST)
    
    def _get_settlement_mode(self, mode: str):
        """Get x402 settlement mode enum."""
        import opengradient as og
        
        mode_map = {
            "PRIVATE": og.x402SettlementMode.PRIVATE,
            "INDIVIDUAL_FULL": og.x402SettlementMode.INDIVIDUAL_FULL,
            "BATCH_HASHED": og.x402SettlementMode.BATCH_HASHED,
        }
        
        return mode_map.get(mode.upper(), og.x402SettlementMode.BATCH_HASHED)
    
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
            llm_response = await self._call_llm(chat_session.messages, request)
            response_content = llm_response.get("content", "")
            
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
                "payment_hash": llm_response.get("payment_hash"),
                "model_used": llm_response.get("model_used"),
                "tool_calls": llm_response.get("tool_calls"),
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        request: ChatRequest,
    ) -> Dict[str, Any]:
        """Call OpenGradient LLM with retry logic."""
        import opengradient as og
        
        model = self._get_model_enum(request.model or "grok-4-fast")
        settlement_mode = self._get_settlement_mode(request.settlement_mode or "BATCH_HASHED")
        
        for attempt in range(3):
            try:
                if request.stream:
                    stream = await self.llm.chat(
                        model=model,
                        messages=messages,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                        tools=request.tools,
                        x402_settlement_mode=settlement_mode,
                        stream=True,
                    )
                    full_content = ""
                    async for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            full_content += chunk.choices[0].delta.content
                    return {"content": full_content, "model_used": request.model or "grok-4-fast", "payment_hash": None}
                else:
                    response = await self.llm.chat(
                        model=model,
                        messages=messages,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                        tools=request.tools,
                        x402_settlement_mode=settlement_mode,
                        stream=False,
                    )
                    return {
                        "content": response.chat_output["content"],
                        "model_used": request.model or "grok-4-fast",
                        "payment_hash": getattr(response, 'payment_hash', None),
                        "tool_calls": response.chat_output.get("tool_calls", None) if isinstance(response.chat_output, dict) else None
                    }
            except Exception as e:
                if attempt < 2:
                    logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(2)
                else:
                    logger.error(f"LLM call failed after 3 attempts: {e}")
                    return {"content": self._get_fallback_response(messages[-1]["content"]), "model_used": request.model or "grok-4-fast", "payment_hash": None}
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Get fallback response when API fails."""
        import random
        fallbacks = [
            "I apologize, but I'm having trouble connecting to the OpenGradient network right now. Please try again in a few moments.",
            "It seems there's an issue with the AI service. You can try searching for models directly on the OpenGradient Model Hub.",
            "I'm experiencing some technical difficulties. Please check your connection and try again.",
        ]
        return random.choice(fallbacks)
    
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
