"""
User stats and achievements service.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from models.db_models import UserStats, UserAchievement


# Achievements configuration
ACHIEVEMENTS = {
    "first_query": {
        "id": "first_query",
        "name": "Первый запрос",
        "description": "Сделайте первый поисковый запрос",
        "icon": "🎯",
        "points": 5,
        "condition": {"total_queries": 1}
    },
    "query_master": {
        "id": "query_master",
        "name": "Мастер поиска",
        "description": "Сделайте 100 поисковых запросов",
        "icon": "🔍",
        "points": 50,
        "condition": {"total_queries": 100}
    },
    "chat_newbie": {
        "id": "chat_newbie",
        "name": "Начинающий чатер",
        "description": "Отправьте 10 сообщений в чате",
        "icon": "💬",
        "points": 10,
        "condition": {"total_chats": 10}
    },
    "chat_expert": {
        "id": "chat_expert",
        "name": "Эксперт чата",
        "description": "Отправьте 100 сообщений в чате",
        "icon": "🎓",
        "points": 50,
        "condition": {"total_chats": 100}
    },
    "model_explorer": {
        "id": "model_explorer",
        "name": "Исследователь моделей",
        "description": "Просмотрите 50 моделей",
        "icon": "👁️",
        "points": 25,
        "condition": {"total_models_viewed": 50}
    },
    "token_collector": {
        "id": "token_collector",
        "name": "Коллекционер токенов",
        "description": "Заработайте 100 токенов",
        "icon": "💎",
        "points": 30,
        "condition": {"total_tokens_earned": 100}
    },
    "streak_7": {
        "id": "streak_7",
        "name": "Недельный стрик",
        "description": "Заходите 7 дней подряд",
        "icon": "🔥",
        "points": 50,
        "condition": {"current_streak": 7}
    },
    "streak_30": {
        "id": "streak_30",
        "name": "Месячный стрик",
        "description": "Заходите 30 дней подряд",
        "icon": "⚡",
        "points": 200,
        "condition": {"current_streak": 30}
    },
    "level_5": {
        "id": "level_5",
        "name": "5 Уровень",
        "description": "Достигните 5 уровня",
        "icon": "⭐",
        "points": 50,
        "condition": {"level": 5}
    },
    "level_10": {
        "id": "level_10",
        "name": "10 Уровень",
        "description": "Достигните 10 уровня",
        "icon": "🌟",
        "points": 100,
        "condition": {"level": 10}
    },
}


class UserStatsService:
    """Service for managing user statistics."""

    async def get_or_create_stats(self, db: AsyncSession, user_id: str) -> UserStats:
        """Get or create user stats."""
        result = await db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
            await db.commit()
            await db.refresh(stats)

        return stats

    async def increment_query(self, db: AsyncSession, user_id: str):
        """Increment query counter."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_queries += 1
        stats.experience += 2  # 2 XP per query
        await self._check_level_up(stats)
        await db.commit()

    async def increment_chat(self, db: AsyncSession, user_id: str):
        """Increment chat counter."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_chats += 1
        stats.experience += 3  # 3 XP per chat
        await self._check_level_up(stats)
        await db.commit()

    async def increment_model_view(self, db: AsyncSession, user_id: str):
        """Increment model view counter."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_models_viewed += 1
        stats.experience += 1  # 1 XP per view
        await self._check_level_up(stats)
        await db.commit()

    async def add_tokens_earned(self, db: AsyncSession, user_id: str, amount: float):
        """Add tokens earned."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_tokens_earned += amount
        stats.experience += int(amount)  # 1 XP per token
        await self._check_level_up(stats)
        await db.commit()

    async def add_tokens_spent(self, db: AsyncSession, user_id: str, amount: float):
        """Add tokens spent."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_tokens_spent += amount
        await db.commit()

    async def add_tokens_claimed(self, db: AsyncSession, user_id: str, amount: float):
        """Add tokens claimed from faucet."""
        stats = await self.get_or_create_stats(db, user_id)
        stats.total_tokens_claimed += amount
        stats.experience += 5  # 5 XP per claim
        await self._check_level_up(stats)
        await db.commit()

    async def update_streak(self, db: AsyncSession, user_id: str):
        """Update user streak (daily login)."""
        stats = await self.get_or_create_stats(db, user_id)
        today = datetime.utcnow().date()
        
        if stats.last_active:
            last_active_date = stats.last_active.date()
            days_diff = (today - last_active_date).days
            
            if days_diff == 1:
                # Continue streak
                stats.current_streak += 1
            elif days_diff > 1:
                # Break streak
                stats.current_streak = 1
            # days_diff == 0 means already active today, don't update
        else:
            stats.current_streak = 1
        
        stats.longest_streak = max(stats.longest_streak, stats.current_streak)
        stats.last_active = datetime.utcnow()
        stats.experience += 10  # 10 XP for daily login
        await self._check_level_up(stats)
        await db.commit()

    def _check_level_up(self, stats: UserStats):
        """Check and process level up."""
        while stats.experience >= stats.experience_to_next_level:
            stats.level += 1
            stats.experience -= stats.experience_to_next_level
            stats.experience_to_next_level = int(stats.experience_to_next_level * 1.5)
            logger.info(f"User {stats.user_id} leveled up to {stats.level}!")

    async def get_stats(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        stats = await self.get_or_create_stats(db, user_id)
        return stats.to_dict()

    async def get_leaderboard(
        self,
        db: AsyncSession,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top users by experience."""
        result = await db.execute(
            select(UserStats)
            .order_by(desc(UserStats.experience))
            .limit(limit)
        )
        stats_list = result.scalars().all()
        return [s.to_dict() for s in stats_list]


class AchievementService:
    """Service for managing user achievements."""

    async def get_user_achievements(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all user achievements."""
        result = await db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(desc(UserAchievement.unlocked_at))
        )
        achievements = result.scalars().all()
        return [a.to_dict() for a in achievements]

    async def check_and_unlock(
        self,
        db: AsyncSession,
        user_id: str,
        stats: UserStats,
    ) -> List[Dict[str, Any]]:
        """Check if any achievements should be unlocked."""
        unlocked = []
        existing = await self.get_user_achievements(db, user_id)
        existing_ids = {a["achievement_id"] for a in existing}

        for achievement_id, achievement in ACHIEVEMENTS.items():
            if achievement_id in existing_ids:
                continue  # Already unlocked

            # Check if condition is met
            if self._check_condition(stats, achievement["condition"]):
                # Unlock achievement
                new_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement_id,
                    achievement_name=achievement["name"],
                    achievement_description=achievement["description"],
                    achievement_icon=achievement["icon"],
                    points=achievement["points"],
                )
                db.add(new_achievement)
                unlocked.append(new_achievement.to_dict())
                logger.info(f"User {user_id} unlocked achievement: {achievement['name']}")

        if unlocked:
            await db.commit()

        return unlocked

    def _check_condition(self, stats: UserStats, condition: Dict[str, Any]) -> bool:
        """Check if stats meet achievement condition."""
        for stat_name, required_value in condition.items():
            current_value = getattr(stats, stat_name, 0)
            if current_value < required_value:
                return False
        return True

    async def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Get all available achievements."""
        return list(ACHIEVEMENTS.values())


# Global service instances
user_stats_service = UserStatsService()
achievement_service = AchievementService()
