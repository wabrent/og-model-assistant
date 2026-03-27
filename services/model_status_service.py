"""
Service for checking live status of AI models.
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import httpx

from models.db_models import Model, ModelStatus


class ModelStatusService:
    """Service for monitoring model availability."""

    def __init__(self):
        self.base_url = "https://hub-api.opengradient.ai"
        self.timeout = 10.0  # seconds

    async def check_model_status(
        self,
        db: AsyncSession,
        model: Model,
    ) -> Dict[str, Any]:
        """
        Check if a model is online and responsive.
        Returns status information.
        """
        start_time = time.time()
        is_online = False
        error_message = None
        response_time_ms = None

        try:
            # Try to fetch model info from API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/v0/models/{model.name}"
                response = await client.get(url)
                
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    is_online = True
                    logger.info(f"Model {model.name} is online ({response_time_ms:.0f}ms)")
                else:
                    error_message = f"HTTP {response.status_code}"
                    logger.warning(f"Model {model.name} returned {response.status_code}")
                    
        except httpx.TimeoutException:
            error_message = "Timeout"
            logger.warning(f"Model {model.name} check timed out")
        except httpx.ConnectError as e:
            error_message = f"Connection error: {str(e)}"
            logger.error(f"Model {model.name} connection failed: {e}")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            logger.error(f"Model {model.name} check failed: {e}")

        # Update or create status record
        status = await self._update_status(
            db, model, is_online, response_time_ms, error_message
        )

        return status.to_dict()

    async def _update_status(
        self,
        db: AsyncSession,
        model: Model,
        is_online: bool,
        response_time_ms: Optional[float],
        error_message: Optional[str],
    ) -> ModelStatus:
        """Update or create model status record."""
        result = await db.execute(
            select(ModelStatus).where(ModelStatus.model_id == model.id)
        )
        status = result.scalar_one_or_none()

        if not status:
            status = ModelStatus(model_id=model.id)
            db.add(status)

        # Update status
        status.is_online = is_online
        status.last_checked = datetime.utcnow()
        status.response_time_ms = response_time_ms
        status.error_message = error_message
        status.checked_at = datetime.utcnow()

        # Update counters
        if is_online:
            status.success_count += 1
        else:
            status.failure_count += 1

        # Calculate uptime (last 100 checks)
        total_checks = status.success_count + status.failure_count
        if total_checks > 0:
            status.uptime_percentage = (status.success_count / total_checks) * 100

        await db.commit()
        await db.refresh(status)

        return status

    async def check_all_models(
        self,
        db: AsyncSession,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Check status of all models.
        Returns summary statistics.
        """
        result = await db.execute(
            select(Model).where(Model.is_active == True)
        )
        models = result.scalars().all()

        if limit:
            models = models[:limit]

        logger.info(f"Checking status of {len(models)} models...")

        online_count = 0
        offline_count = 0
        total_response_time = 0

        for model in models:
            status_dict = await self.check_model_status(db, model)
            
            if status_dict["is_online"]:
                online_count += 1
                if status_dict["response_time_ms"]:
                    total_response_time += status_dict["response_time_ms"]
            else:
                offline_count += 1

            # Rate limiting
            await asyncio.sleep(0.2)

        avg_response_time = (
            total_response_time / online_count if online_count > 0 else 0
        )

        logger.info(
            f"Status check complete: {online_count} online, "
            f"{offline_count} offline, avg {avg_response_time:.0f}ms"
        )

        return {
            "total_models": len(models),
            "online": online_count,
            "offline": offline_count,
            "avg_response_time_ms": round(avg_response_time, 2),
            "uptime_percentage": round((online_count / len(models)) * 100, 2) if models else 0,
        }

    async def get_model_status(
        self,
        db: AsyncSession,
        model_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Get current status of a model."""
        result = await db.execute(
            select(ModelStatus).where(ModelStatus.model_id == model_id)
        )
        status = result.scalar_one_or_none()

        if not status:
            return None

        return status.to_dict()

    async def get_online_models(
        self,
        db: AsyncSession,
    ) -> List[Dict[str, Any]]:
        """Get list of online models."""
        result = await db.execute(
            select(ModelStatus)
            .where(ModelStatus.is_online == True)
            .order_by(ModelStatus.response_time_ms)
        )
        statuses = result.scalars().all()

        return [s.to_dict() for s in statuses]

    async def get_status_summary(self, db: AsyncSession) -> Dict[str, Any]:
        """Get summary of all model statuses."""
        # Default response if table doesn't exist or any error occurs
        default_response = {
            "total_models": 0,
            "online": 0,
            "offline": 0,
            "avg_response_time_ms": 0,
            "avg_uptime_percentage": 0,
        }
        
        try:
            result = await db.execute(
                select(
                    func.count(ModelStatus.id).label("total"),
                    func.sum(func.case((ModelStatus.is_online == True, 1), else_=0)).label("online"),
                    func.sum(func.case((ModelStatus.is_online == False, 1), else_=0)).label("offline"),
                    func.avg(ModelStatus.response_time_ms).label("avg_response"),
                    func.avg(ModelStatus.uptime_percentage).label("avg_uptime"),
                )
            )
            row = result.first()

            return {
                "total_models": row.total or 0,
                "online": row.online or 0,
                "offline": row.offline or 0,
                "avg_response_time_ms": round(row.avg_response or 0, 2),
                "avg_uptime_percentage": round(row.avg_uptime or 0, 2),
            }
        except Exception as e:
            # Table doesn't exist yet - return default values
            logger.warning(f"Status summary failed (table may not exist): {e}")
            return default_response


# Global service instance
model_status_service = ModelStatusService()
