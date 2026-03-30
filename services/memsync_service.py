"""
MemSync service for long-term AI memory and personalization.
"""
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

from core.config import settings


class MemSyncService:
    """Service for interacting with MemSync API."""
    
    BASE_URL = "https://api.memchat.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.memsync_api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key or "",
            "Content-Type": "application/json"
        }
    
    async def store_memory(
        self,
        messages: List[Dict[str, str]],
        agent_id: str = "og-assistant",
        thread_id: Optional[str] = None,
        source: str = "chat"
    ) -> Dict[str, Any]:
        """Store conversation to extract memories."""
        if not self.api_key:
            return {"status": "disabled", "message": "MemSync API key not configured"}
        
        try:
            data = {
                "messages": messages,
                "agent_id": agent_id,
                "source": source
            }
            if thread_id:
                data["thread_id"] = thread_id
            
            response = await self.client.post(
                f"{self.BASE_URL}/memories",
                json=data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MemSync store error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        rerank: bool = True
    ) -> Dict[str, Any]:
        """Search for relevant memories."""
        if not self.api_key:
            return {"memories": [], "user_bio": ""}
        
        try:
            data = {
                "query": query,
                "limit": limit,
                "rerank": rerank
            }
            response = await self.client.post(
                f"{self.BASE_URL}/memories/search",
                json=data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MemSync search error: {e}")
            return {"memories": [], "user_bio": "", "error": str(e)}
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile with bio and insights."""
        if not self.api_key:
            return {"user_bio": "", "profiles": [], "insights": []}
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/users/profile",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MemSync profile error: {e}")
            return {"user_bio": "", "profiles": [], "insights": [], "error": str(e)}
    
    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a specific memory."""
        if not self.api_key:
            return {"status": "disabled"}
        
        try:
            response = await self.client.delete(
                f"{self.BASE_URL}/memories/{memory_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"status": "deleted", "memory_id": memory_id}
        except Exception as e:
            logger.error(f"MemSync delete error: {e}")
            return {"status": "error", "message": str(e)}


memsync_service = MemSyncService()


async def get_memsync_service() -> MemSyncService:
    return memsync_service
