"""
OpenGradient API service for fetching and syncing models.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from models.db_models import Model
from core.database import async_session_maker
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert


class OpenGradientService:
    """Service for interacting with OpenGradient API."""
    
    BASE_URL = "https://hub-api.opengradient.ai"
    API_TIMEOUT = 30
    
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.API_TIMEOUT,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def fetch_all_models(self) -> List[Dict[str, Any]]:
        """
        Fetch all models from OpenGradient Hub API.
        Handles pagination automatically.
        """
        all_models = []
        page = 0
        limit = 100
        
        while True:
            try:
                url = f"{self.BASE_URL}/api/v0/models/"
                params = {"page": page, "limit": limit}
                
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                batch = data.get("models", data) if isinstance(data, dict) else data
                if not batch:
                    break
                
                all_models.extend(batch)
                logger.info(f"Fetched page {page}, got {len(batch)} models")
                
                if len(batch) < limit:
                    break
                
                page += 1
                await asyncio.sleep(0.5)  # Rate limiting
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error on page {page}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                raise
        
        logger.info(f"Total models fetched: {len(all_models)}")
        return all_models
    
    async def fetch_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch a single model by name."""
        try:
            url = f"{self.BASE_URL}/api/v0/models/{name}"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching model {name}: {e}")
            return None
    
    async def sync_models(self) -> Dict[str, Any]:
        """
        Sync models from API to database.
        Returns sync statistics.
        """
        start_time = datetime.utcnow()
        stats = {
            "fetched": 0,
            "new": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0,
        }
        
        try:
            # Fetch all models from API
            fresh_models = await self.fetch_all_models()
            stats["fetched"] = len(fresh_models)
            
            async with async_session_maker() as session:
                for model_data in fresh_models:
                    try:
                        await self._upsert_model(session, model_data)
                        stats["new"] += 1  # Simplified - would need to track insert vs update
                    except Exception as e:
                        logger.error(f"Error upserting model {model_data.get('name')}: {e}")
                        stats["errors"] += 1
                
                await session.commit()
            
            stats["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Sync completed: {stats}")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            stats["error_message"] = str(e)
        
        return stats
    
    async def _upsert_model(self, session, model_data: Dict[str, Any]):
        """Insert or update a single model."""
        from sqlalchemy import select
        
        name = model_data.get("name")
        if not name:
            return
        
        # Check if model exists
        result = await session.execute(
            select(Model).where(Model.name == name)
        )
        existing_model = result.scalar_one_or_none()
        
        # Prepare model data
        model_dict = {
            "name": name,
            "task_name": model_data.get("taskName"),
            "description": model_data.get("description"),
            "author_username": model_data.get("authorUsername"),
            "author_address": model_data.get("authorAddress"),
            "model_address": model_data.get("modelAddress"),
            "tags": model_data.get("tags", []),
            "is_active": True,
        }
        
        if existing_model:
            # Update existing
            for key, value in model_dict.items():
                setattr(existing_model, key, value)
            existing_model.updated_at = datetime.utcnow()
        else:
            # Insert new
            new_model = Model(**model_dict)
            session.add(new_model)


# Global service instance
og_service = OpenGradientService()


async def get_og_service() -> OpenGradientService:
    """Dependency for getting OpenGradient service."""
    return og_service
