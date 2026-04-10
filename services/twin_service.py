"""
TwinFun service for OpenGradient Digital Twins integration.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings
import opengradient as og


class TwinService:
    """Service for interacting with OpenGradient Digital Twins (TwinFun)."""
    
    TWINS_API_BASE_URL = "https://chat-api.memchat.io"
    API_TIMEOUT = 30
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.twins_api_key or settings.memsync_api_key
        self._twins_client: Optional[og.Twins] = None
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @property
    def twins_client(self) -> Optional[og.Twins]:
        """Get or create Twins client."""
        if self._twins_client is None and self.api_key:
            try:
                self._twins_client = og.Twins(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to create Twins client: {e}")
        return self._twins_client
    
    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=self.API_TIMEOUT,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-API-Key": self.api_key if self.api_key else "",
                }
            )
        return self._http_client
    
    async def close(self):
        """Close HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
    
    async def get_available_twins(self) -> List[Dict[str, Any]]:
        """
        Get list of available digital twins.
        
        Returns:
            List of twin objects with id, name, description, etc.
        """
        try:
            # Try to fetch from TwinFun API
            url = f"{self.TWINS_API_BASE_URL}/api/v1/twins"
            response = await self.http_client.get(url)
            
            if response.status_code == 200:
                twins = response.json()
                logger.info(f"Fetched {len(twins)} twins from API")
                return twins
            else:
                logger.warning(f"Failed to fetch twins: {response.status_code}")
                # Fallback to mock data
                return self._mock_twins()
                
        except Exception as e:
            logger.error(f"Error fetching twins: {e}")
            return self._mock_twins()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def chat_with_twin(
        self,
        twin_id: str,
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Chat with a digital twin.
        
        Args:
            twin_id: Unique identifier of the twin
            message: User message
            model: TEE LLM model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with chat response
        """
        try:
            # Try to use OpenGradient SDK Twins client
            if self.twins_client:
                # Convert model string to TEE_LLM enum if needed
                tee_model = self._get_tee_llm_model(model)
                
                messages = [{"role": "user", "content": message}]
                
                logger.info(f"Chatting with twin {twin_id} using SDK")
                result = self.twins_client.chat(
                    twin_id=twin_id,
                    model=tee_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return {
                    "twin_id": twin_id,
                    "message": message,
                    "response": result.chat_output.get("content", "") if result.chat_output else "",
                    "model": model or "default",
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "OpenGradient SDK",
                    "finish_reason": result.finish_reason
                }
            else:
                # Fallback to direct HTTP API
                return await self._chat_via_http(twin_id, message, model, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"Error chatting with twin {twin_id}: {e}")
            # Fallback to mock response
            return self._mock_chat_response(twin_id, message, model)
    
    async def _chat_via_http(
        self,
        twin_id: str,
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Chat with twin via direct HTTP API."""
        url = f"{self.TWINS_API_BASE_URL}/api/v1/twins/{twin_id}/chat"
        
        payload = {
            "model": model or "anthropic/claude-haiku-4-5",
            "messages": [{"role": "user", "content": message}]
        }
        
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            choices = result.get("choices", [])
            if choices:
                message_content = choices[0].get("message", {}).get("content", "")
                finish_reason = choices[0].get("finish_reason")
            else:
                message_content = "No response"
                finish_reason = None
            
            return {
                "twin_id": twin_id,
                "message": message,
                "response": message_content,
                "model": model or "default",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "HTTP API",
                "finish_reason": finish_reason
            }
            
        except Exception as e:
            logger.error(f"HTTP API chat failed: {e}")
            raise
    
    def _get_tee_llm_model(self, model_str: Optional[str] = None) -> og.types.TEE_LLM:
        """Convert model string to TEE_LLM enum."""
        if model_str:
            # Try to find matching enum
            for model_enum in og.TEE_LLM:
                if model_enum.value == model_str or model_enum.name.lower() == model_str.lower().replace("-", "_"):
                    return model_enum
        
        # Default model
        return og.TEE_LLM.CLAUDE_HAIKU_4_5
    
    def _mock_twins(self) -> List[Dict[str, Any]]:
        """Return mock twins for demo purposes."""
        return [
            {
                "id": "defi_analyst_001",
                "name": "DeFi Analyst Pro",
                "description": "AI-powered DeFi market analyst with real-time insights",
                "category": "finance",
                "author": "OpenGradient",
                "tags": ["defi", "trading", "analysis", "crypto"],
                "avatar_url": "https://twin.fun/avatars/defi-analyst.png",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "risk_manager_002",
                "name": "Risk Management Expert",
                "description": "Portfolio risk assessment and optimization specialist",
                "category": "finance",
                "author": "OpenGradient",
                "tags": ["risk", "portfolio", "optimization", "defi"],
                "avatar_url": "https://twin.fun/avatars/risk-manager.png",
                "created_at": "2024-02-20T14:45:00Z"
            },
            {
                "id": "crypto_trader_003",
                "name": "Crypto Trading Assistant",
                "description": "AI trading assistant for cryptocurrency markets",
                "category": "trading",
                "author": "OpenGradient",
                "tags": ["trading", "crypto", "markets", "signals"],
                "avatar_url": "https://twin.fun/avatars/crypto-trader.png",
                "created_at": "2024-03-10T09:15:00Z"
            },
            {
                "id": "market_researcher_004",
                "name": "Market Research Analyst",
                "description": "Deep market analysis and trend forecasting",
                "category": "research",
                "author": "OpenGradient",
                "tags": ["research", "analysis", "trends", "forecasting"],
                "avatar_url": "https://twin.fun/avatars/market-researcher.png",
                "created_at": "2024-04-05T16:20:00Z"
            }
        ]
    
    def _mock_chat_response(
        self,
        twin_id: str,
        message: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate mock chat response for demo."""
        twin_responses = {
            "defi_analyst_001": "Based on current market conditions, ETH shows strong support at $3,400 with resistance at $3,800. The RSI indicates neutral momentum. Consider dollar-cost averaging for long-term positions.",
            "risk_manager_002": "Your portfolio exhibits moderate risk concentration in high-volatility assets. I recommend increasing stablecoin exposure to 20% and adding hedging positions for downside protection.",
            "crypto_trader_003": "SUI/USDT shows bullish divergence on the 4H chart. Entry around $1.20 with stop loss at $1.15 could yield a 15-20% upside to $1.40 resistance.",
            "market_researcher_004": "Current DeFi TVL growth suggests institutional accumulation. Look for protocols with sustainable tokenomics and real revenue generation rather than speculative plays."
        }
        
        default_response = "As a digital twin specialized in DeFi analysis, I recommend conducting thorough due diligence before any investment decisions. Consider market conditions, tokenomics, and risk tolerance."
        
        response = twin_responses.get(twin_id, default_response)
        
        return {
            "twin_id": twin_id,
            "message": message,
            "response": response,
            "model": model or "mock/model",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Mock Data",
            "finish_reason": "stop",
            "note": "Enable TwinFun API key for real responses"
        }
    
    async def analyze_portfolio_with_twin(
        self,
        portfolio_data: Dict[str, Any],
        twin_id: str = "defi_analyst_001"
    ) -> Dict[str, Any]:
        """
        Analyze portfolio using a DeFi analyst twin.
        
        Args:
            portfolio_data: Portfolio information
            twin_id: Twin to use for analysis
            
        Returns:
            Analysis results
        """
        # Prepare analysis request
        assets = portfolio_data.get("assets", [])
        total_value = portfolio_data.get("total_value", 0)
        
        message = f"""
        Please analyze this DeFi portfolio:
        
        Total Value: ${total_value:,.2f}
        Assets: {len(assets)}
        
        Asset Breakdown:
        {json.dumps(assets[:10], indent=2)}
        
        Provide insights on:
        1. Risk assessment
        2. Diversification score
        3. Recommended adjustments
        4. Market outlook implications
        """
        
        response = await self.chat_with_twin(
            twin_id=twin_id,
            message=message,
            model="anthropic/claude-sonnet-4-6"
        )
        
        return {
            "portfolio_id": portfolio_data.get("id", "unknown"),
            "twin_id": twin_id,
            "analysis": response["response"],
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "assets_analyzed": len(assets),
                "total_value": total_value,
                "model_used": response.get("model")
            }
        }


# Global instance
twin_service = TwinService()