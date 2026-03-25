"""
Model service for database operations and search.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from models.db_models import Model, ModelAnalytics
from models.schemas import ModelSearchRequest


class ModelService:
    """Service for model database operations."""
    
    async def search_models(
        self,
        db: AsyncSession,
        search_request: ModelSearchRequest,
    ) -> Tuple[List[Model], int]:
        """
        Search models with filters and full-text search.
        Returns tuple of (models, total_count).
        """
        # Build base query
        query = select(Model).where(Model.is_active == True)
        count_query = select(func.count()).select_from(Model).where(Model.is_active == True)
        
        # Apply filters
        filters = []
        
        if search_request.query:
            # Full-text search across multiple fields
            query_text = search_request.query.lower()
            filters.append(
                or_(
                    Model.name.ilike(f"%{query_text}%"),
                    Model.description.ilike(f"%{query_text}%"),
                    Model.task_name.ilike(f"%{query_text}%"),
                    Model.author_username.ilike(f"%{query_text}%"),
                )
            )
        
        if search_request.task_name:
            filters.append(Model.task_name.ilike(f"%{search_request.task_name}%"))
        
        if search_request.author_username:
            filters.append(Model.author_username.ilike(f"%{search_request.author_username}%"))
        
        if search_request.tags:
            # Search within JSON tags array
            for tag in search_request.tags:
                filters.append(
                    Model.tags.cast(str).ilike(f"%{tag}%")
                )
        
        # Apply filters
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Apply sorting
        if search_request.sort_by == "name":
            order_col = Model.name
        elif search_request.sort_by == "created_at":
            order_col = Model.created_at
        elif search_request.sort_by == "popularity":
            # Join with analytics for popularity
            query = query.outerjoin(
                ModelAnalytics,
                Model.id == ModelAnalytics.model_id
            ).order_by(
                func.coalesce(ModelAnalytics.selections_count, 0).desc()
            )
            order_col = None
        else:  # relevance - default
            order_col = Model.created_at
        
        if order_col:
            if search_request.sort_order == "desc":
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col.asc())
        
        # Apply pagination
        query = query.offset(search_request.offset).limit(search_request.limit)
        
        # Execute queries
        result = await db.execute(query)
        models = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return models, total
    
    async def get_model_by_id(self, db: AsyncSession, model_id: int) -> Optional[Model]:
        """Get model by ID."""
        result = await db.execute(select(Model).where(Model.id == model_id))
        return result.scalar_one_or_none()
    
    async def get_model_by_name(self, db: AsyncSession, name: str) -> Optional[Model]:
        """Get model by name."""
        result = await db.execute(select(Model).where(Model.name == name))
        return result.scalar_one_or_none()
    
    async def get_all_models(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Model], int]:
        """Get all models with pagination."""
        query = select(Model).where(Model.is_active == True)
        count_query = select(func.count()).select_from(Model).where(Model.is_active == True)
        
        query = query.order_by(Model.name.asc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        models = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return models, total
    
    async def get_unique_tasks(self, db: AsyncSession) -> List[str]:
        """Get list of unique task names."""
        result = await db.execute(
            select(Model.task_name)
            .where(Model.task_name.isnot(None))
            .where(Model.is_active == True)
            .distinct()
        )
        return [row[0] for row in result.all() if row[0]]
    
    async def get_unique_authors(self, db: AsyncSession) -> List[str]:
        """Get list of unique author usernames."""
        result = await db.execute(
            select(Model.author_username)
            .where(Model.author_username.isnot(None))
            .where(Model.is_active == True)
            .distinct()
        )
        return [row[0] for row in result.all() if row[0]]
    
    async def get_all_tags(self, db: AsyncSession) -> List[str]:
        """Get all unique tags from all models."""
        result = await db.execute(
            select(Model.tags).where(Model.is_active == True)
        )
        all_tags = set()
        for row in result.all():
            if row[0]:
                all_tags.update(row[0])
        return sorted(list(all_tags))
    
    async def increment_view(self, db: AsyncSession, model_id: int):
        """Increment view count for a model."""
        analytics = await self._get_or_create_analytics(db, model_id)
        analytics.views_count += 1
        analytics.last_viewed_at = datetime.utcnow()
        await db.commit()
    
    async def increment_query(self, db: AsyncSession, model_id: int):
        """Increment query count for a model."""
        analytics = await self._get_or_create_analytics(db, model_id)
        analytics.queries_count += 1
        await db.commit()
    
    async def increment_selection(self, db: AsyncSession, model_id: int):
        """Increment selection count for a model."""
        analytics = await self._get_or_create_analytics(db, model_id)
        analytics.selections_count += 1
        analytics.last_selected_at = datetime.utcnow()
        await db.commit()
    
    async def _get_or_create_analytics(
        self,
        db: AsyncSession,
        model_id: int,
    ) -> ModelAnalytics:
        """Get or create analytics record for a model."""
        result = await db.execute(
            select(ModelAnalytics).where(ModelAnalytics.model_id == model_id)
        )
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            analytics = ModelAnalytics(model_id=model_id)
            db.add(analytics)
            await db.commit()
            await db.refresh(analytics)
        
        return analytics
    
    async def get_model_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall model statistics."""
        # Total models
        total_result = await db.execute(
            select(func.count()).select_from(Model)
        )
        total = total_result.scalar()
        
        # Active models
        active_result = await db.execute(
            select(func.count()).select_from(Model).where(Model.is_active == True)
        )
        active = active_result.scalar()
        
        # Models by task
        task_result = await db.execute(
            select(Model.task_name, func.count())
            .where(Model.task_name.isnot(None))
            .where(Model.is_active == True)
            .group_by(Model.task_name)
            .order_by(func.count().desc())
        )
        tasks = {row[0]: row[1] for row in task_result.all()}
        
        # Models by author
        author_result = await db.execute(
            select(Model.author_username, func.count())
            .where(Model.author_username.isnot(None))
            .where(Model.is_active == True)
            .group_by(Model.author_username)
            .order_by(func.count().desc())
            .limit(20)
        )
        authors = {row[0]: row[1] for row in author_result.all()}
        
        return {
            "total_models": total,
            "active_models": active,
            "tasks": tasks,
            "top_authors": authors,
        }


# Global service instance
model_service = ModelService()
