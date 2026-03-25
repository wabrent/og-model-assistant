"""
Analytics service for statistics and insights.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from models.db_models import (
    Model, UserQuery, ChatSession, ModelAnalytics,
    GlobalAnalytics
)


class AnalyticsService:
    """Service for analytics and statistics."""
    
    async def get_global_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get global statistics."""
        # Total models
        total_models = await db.scalar(
            select(func.count()).select_from(Model)
        )
        
        # Active models
        active_models = await db.scalar(
            select(func.count())
            .select_from(Model)
            .where(Model.is_active == True)
        )
        
        # Total queries (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        total_queries_result = await db.execute(
            select(func.count())
            .select_from(UserQuery)
            .where(UserQuery.created_at >= thirty_days_ago)
        )
        total_queries = total_queries_result.scalar()
        
        # Total active sessions
        total_sessions = await db.scalar(
            select(func.count())
            .select_from(ChatSession)
            .where(ChatSession.is_active == True)
        )
        
        # Unique users (last 30 days)
        unique_users_result = await db.execute(
            select(func.count(func.distinct(UserQuery.session_id)))
            .where(UserQuery.created_at >= thirty_days_ago)
        )
        unique_users = unique_users_result.scalar()
        
        # Average response time (last 30 days)
        avg_response_result = await db.execute(
            select(func.avg(UserQuery.response_time_ms))
            .where(UserQuery.created_at >= thirty_days_ago)
            .where(UserQuery.response_time_ms.isnot(None))
        )
        avg_response_time = avg_response_result.scalar()
        
        # Top tasks
        tasks_result = await db.execute(
            select(Model.task_name, func.count())
            .where(Model.task_name.isnot(None))
            .where(Model.is_active == True)
            .group_by(Model.task_name)
            .order_by(func.count().desc())
            .limit(10)
        )
        top_tasks = {row[0]: row[1] for row in tasks_result.all()}
        
        # Top authors
        authors_result = await db.execute(
            select(Model.author_username, func.count())
            .where(Model.author_username.isnot(None))
            .where(Model.is_active == True)
            .group_by(Model.author_username)
            .order_by(func.count().desc())
            .limit(10)
        )
        top_authors = {row[0]: row[1] for row in authors_result.all()}
        
        return {
            "total_models": total_models or 0,
            "active_models": active_models or 0,
            "total_queries": total_queries or 0,
            "total_sessions": total_sessions or 0,
            "unique_users": unique_users or 0,
            "avg_response_time_ms": float(avg_response_time) if avg_response_time else None,
            "top_tasks": top_tasks,
            "top_authors": top_authors,
        }
    
    async def get_top_queries(
        self,
        db: AsyncSession,
        period: str = "7d",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get most popular queries."""
        period_start = self._parse_period(period)
        
        result = await db.execute(
            select(
                UserQuery.query_text,
                func.count().label("count"),
                func.avg(UserQuery.response_time_ms).label("avg_time"),
            )
            .where(UserQuery.created_at >= period_start)
            .group_by(UserQuery.query_text)
            .order_by(desc("count"))
            .limit(limit)
        )
        
        return [
            {
                "query": row.query_text,
                "count": row.count,
                "avg_response_time_ms": float(row.avg_time) if row.avg_time else None,
            }
            for row in result.all()
        ]
    
    async def get_popular_models(
        self,
        db: AsyncSession,
        period: str = "7d",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get most popular models by selections."""
        result = await db.execute(
            select(
                Model.id,
                Model.name,
                Model.task_name,
                Model.author_username,
                ModelAnalytics.selections_count,
                ModelAnalytics.views_count,
                ModelAnalytics.queries_count,
            )
            .join(ModelAnalytics, Model.id == ModelAnalytics.model_id)
            .where(Model.is_active == True)
            .order_by(desc(ModelAnalytics.selections_count))
            .limit(limit)
        )
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "task_name": row.task_name,
                "author_username": row.author_username,
                "selections_count": row.selections_count,
                "views_count": row.views_count,
                "queries_count": row.queries_count,
            }
            for row in result.all()
        ]
    
    async def get_query_stats(
        self,
        db: AsyncSession,
        period: str = "7d",
    ) -> Dict[str, Any]:
        """Get query statistics for a period."""
        period_start = self._parse_period(period)
        
        # Total queries
        total_result = await db.execute(
            select(func.count())
            .select_from(UserQuery)
            .where(UserQuery.created_at >= period_start)
        )
        total = total_result.scalar()
        
        # Queries by type
        type_result = await db.execute(
            select(UserQuery.query_type, func.count())
            .where(UserQuery.created_at >= period_start)
            .group_by(UserQuery.query_type)
        )
        by_type = {row.query_type: row.count for row in type_result.all()}
        
        # Average response time
        avg_result = await db.execute(
            select(func.avg(UserQuery.response_time_ms))
            .where(UserQuery.created_at >= period_start)
            .where(UserQuery.response_time_ms.isnot(None))
        )
        avg_time = avg_result.scalar()
        
        # Queries per day (last 7 days)
        daily_result = await db.execute(
            select(
                func.date(UserQuery.created_at).label("date"),
                func.count().label("count"),
            )
            .where(UserQuery.created_at >= datetime.utcnow() - timedelta(days=7))
            .group_by(func.date(UserQuery.created_at))
            .order_by(func.date(UserQuery.created_at))
        )
        daily = {str(row.date): row.count for row in daily_result.all()}
        
        return {
            "total_queries": total or 0,
            "by_type": by_type,
            "avg_response_time_ms": float(avg_time) if avg_time else None,
            "daily_queries": daily,
        }
    
    async def get_model_analytics(
        self,
        db: AsyncSession,
        model_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific model."""
        result = await db.execute(
            select(ModelAnalytics).where(ModelAnalytics.model_id == model_id)
        )
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            return None
        
        return {
            "model_id": analytics.model_id,
            "views_count": analytics.views_count,
            "queries_count": analytics.queries_count,
            "selections_count": analytics.selections_count,
            "last_viewed_at": analytics.last_viewed_at.isoformat() if analytics.last_viewed_at else None,
            "last_selected_at": analytics.last_selected_at.isoformat() if analytics.last_selected_at else None,
        }
    
    async def track_query(
        self,
        db: AsyncSession,
        session_id: str,
        query_text: str,
        query_type: str = "search",
        results_count: int = 0,
        response_time_ms: Optional[float] = None,
        selected_model_id: Optional[int] = None,
    ):
        """Track a user query for analytics."""
        user_query = UserQuery(
            session_id=session_id,
            query_text=query_text,
            query_type=query_type,
            results_count=results_count,
            response_time_ms=response_time_ms,
            selected_model_id=selected_model_id,
        )
        db.add(user_query)
        
        # If model was selected, increment its counter
        if selected_model_id:
            from services.model_service import model_service
            await model_service.increment_selection(db, selected_model_id)
        
        await db.commit()
    
    def _parse_period(self, period: str) -> datetime:
        """Parse period string to datetime."""
        now = datetime.utcnow()
        
        if period.endswith("h"):
            hours = int(period[:-1])
            return now - timedelta(hours=hours)
        elif period.endswith("d"):
            days = int(period[:-1])
            return now - timedelta(days=days)
        elif period.endswith("w"):
            weeks = int(period[:-1])
            return now - timedelta(weeks=weeks)
        elif period.endswith("30d"):
            return now - timedelta(days=30)
        else:
            # Default to 7 days
            return now - timedelta(days=7)


# Global service instance
analytics_service = AnalyticsService()
