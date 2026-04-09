"""
SQLAlchemy models for the application.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, Index, func, JSON
)
from sqlalchemy.orm import relationship

from core.database import Base


class Model(Base):
    """AI Model from OpenGradient Hub."""
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    task_name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    author_username = Column(String(100), nullable=True, index=True)
    author_address = Column(String(100), nullable=True)
    model_address = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True, default=list)

    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    queries = relationship("UserQuery", back_populates="model", lazy="select")
    analytics = relationship("ModelAnalytics", back_populates="model", uselist=False, lazy="select")

    __table_args__ = (
        Index('ix_models_task_author', 'task_name', 'author_username'),
    )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "task_name": self.task_name,
            "description": self.description,
            "author_username": self.author_username,
            "author_address": self.author_address,
            "model_address": self.model_address,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }


class UserQuery(Base):
    """User search/query history."""
    __tablename__ = "user_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), default="search")  # search, chat, filter
    
    # Results
    results_count = Column(Integer, default=0)
    selected_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Float, nullable=True)
    query_metadata = Column(JSON, nullable=True, default=dict)

    # Relationships
    model = relationship("Model", back_populates="queries")
    
    __table_args__ = (
        Index('ix_queries_session_created', 'session_id', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        """Convert query to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "query_text": self.query_text,
            "query_type": self.query_type,
            "results_count": self.results_count,
            "selected_model_id": self.selected_model_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "response_time_ms": self.response_time_ms,
        }


class ChatSession(Base):
    """Chat session for conversation history."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)  # Optional user identification
    
    # Messages stored as JSON array
    messages = Column(JSON, nullable=True, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('ix_sessions_user_active', 'user_id', 'is_active'),
    )
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "message_count": self.message_count,
        }


class ModelAnalytics(Base):
    """Analytics for each model."""
    __tablename__ = "model_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), unique=True, nullable=False)
    
    # Counters
    views_count = Column(Integer, default=0)
    queries_count = Column(Integer, default=0)
    selections_count = Column(Integer, default=0)
    
    # Time tracking
    last_viewed_at = Column(DateTime, nullable=True)
    last_selected_at = Column(DateTime, nullable=True)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model = relationship("Model", back_populates="analytics")
    
    def to_dict(self) -> dict:
        """Convert analytics to dictionary."""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "views_count": self.views_count,
            "queries_count": self.queries_count,
            "selections_count": self.selections_count,
            "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            "last_selected_at": self.last_selected_at.isoformat() if self.last_selected_at else None,
        }


class GlobalAnalytics(Base):
    """Global analytics and statistics."""
    __tablename__ = "global_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), unique=True, nullable=False)
    metric_value = Column(JSON, nullable=False)
    
    # Time period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert analytics to dictionary."""
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
        }


class UserToken(Base):
    """User tokens/credits for API usage."""
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # session_id or wallet address
    balance = Column(Float, default=10.0)  # Free 10 tokens to start
    total_purchased = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    last_faucet_claim = Column(DateTime, nullable=True)  # Last faucet claim time
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "user_id": self.user_id,
            "balance": self.balance,
            "total_purchased": self.total_purchased,
            "total_spent": self.total_spent,
            "last_faucet_claim": self.last_faucet_claim.isoformat() if self.last_faucet_claim else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TokenTransaction(Base):
    """Token transaction history."""
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, spend, refund, bonus
    description = Column(Text, nullable=True)
    balance_after = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserAchievement(Base):
    """User achievements and milestones."""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False)  # achievement identifier
    achievement_name = Column(String(100), nullable=False)
    achievement_description = Column(Text, nullable=True)
    achievement_icon = Column(String(50), nullable=True)  # emoji icon
    points = Column(Integer, default=0)  # achievement points
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert achievement to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "achievement_name": self.achievement_name,
            "achievement_description": self.achievement_description,
            "achievement_icon": self.achievement_icon,
            "points": self.points,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
        }


class UserStats(Base):
    """User statistics and activity tracking."""
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # Activity stats
    total_queries = Column(Integer, default=0)  # Total search queries
    total_chats = Column(Integer, default=0)  # Total chat messages
    total_models_viewed = Column(Integer, default=0)  # Models viewed
    total_favorites = Column(Integer, default=0)  # Models favorited
    
    # Token stats
    total_tokens_earned = Column(Float, default=0.0)
    total_tokens_spent = Column(Float, default=0.0)
    total_tokens_claimed = Column(Float, default=0.0)
    
    # Streak stats
    current_streak = Column(Integer, default=0)  # Current daily streak
    longest_streak = Column(Integer, default=0)  # Longest streak
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Level and progress
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    experience_to_next_level = Column(Integer, default=100)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_queries": self.total_queries,
            "total_chats": self.total_chats,
            "total_models_viewed": self.total_models_viewed,
            "total_favorites": self.total_favorites,
            "total_tokens_earned": self.total_tokens_earned,
            "total_tokens_spent": self.total_tokens_spent,
            "total_tokens_claimed": self.total_tokens_claimed,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "level": self.level,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelStatus(Base):
    """Live status of AI models - online/offline tracking."""
    __tablename__ = "model_statuses"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), unique=True, nullable=False, index=True)
    
    # Status tracking
    is_online = Column(Boolean, default=True)  # Current online status
    last_checked = Column(DateTime, default=datetime.utcnow)  # Last check time
    response_time_ms = Column(Float, nullable=True)  # Last response time
    uptime_percentage = Column(Float, default=100.0)  # Uptime % (last 24h)
    
    # Health metrics
    success_count = Column(Integer, default=0)  # Successful checks
    failure_count = Column(Integer, default=0)  # Failed checks
    error_message = Column(Text, nullable=True)  # Last error message
    
    # Metadata
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    model = relationship("Model", backref="status", uselist=False, lazy="select")

    def to_dict(self) -> dict:
        """Convert status to dictionary."""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "is_online": self.is_online,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "response_time_ms": self.response_time_ms,
            "uptime_percentage": round(self.uptime_percentage, 2),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "error_message": self.error_message,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }


# ============== DeFi Models ==============

class Portfolio(Base):
    """User DeFi portfolio."""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # wallet address
    name = Column(String(100), default="My Portfolio")
    description = Column(Text, nullable=True)
    
    # Total portfolio value
    total_value_usd = Column(Float, default=0.0)
    total_value_change_24h = Column(Float, default=0.0)  # in USD
    total_value_change_percent_24h = Column(Float, default=0.0)  # in percentage
    
    # Performance metrics
    daily_pnl = Column(Float, default=0.0)
    weekly_pnl = Column(Float, default=0.0)
    monthly_pnl = Column(Float, default=0.0)
    all_time_pnl = Column(Float, default=0.0)
    
    # Risk metrics
    volatility_30d = Column(Float, default=0.0)  # 30-day volatility
    sharpe_ratio = Column(Float, default=0.0)  # Sharpe ratio (risk-adjusted return)
    max_drawdown = Column(Float, default=0.0)  # Maximum drawdown
    
    # Asset allocation
    asset_distribution = Column(JSON, nullable=True, default=dict)  # {asset: percentage}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)  # Last portfolio sync time
    
    # Relationships
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    staking_positions = relationship("StakingPosition", back_populates="portfolio", cascade="all, delete-orphan")
    liquidity_positions = relationship("LiquidityPosition", back_populates="portfolio", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "total_value_usd": round(self.total_value_usd, 2),
            "total_value_change_24h": round(self.total_value_change_24h, 2),
            "total_value_change_percent_24h": round(self.total_value_change_percent_24h, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "weekly_pnl": round(self.weekly_pnl, 2),
            "monthly_pnl": round(self.monthly_pnl, 2),
            "all_time_pnl": round(self.all_time_pnl, 2),
            "volatility_30d": round(self.volatility_30d, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "asset_distribution": self.asset_distribution or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "asset_count": len(self.assets) if self.assets else 0,
            "staking_count": len(self.staking_positions) if self.staking_positions else 0,
            "liquidity_count": len(self.liquidity_positions) if self.liquidity_positions else 0,
        }


class Asset(Base):
    """Individual asset in a portfolio."""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Asset identification
    symbol = Column(String(20), nullable=False, index=True)  # BTC, ETH, etc.
    name = Column(String(100), nullable=False)  # Bitcoin, Ethereum
    blockchain = Column(String(50), nullable=True)  # Ethereum, Solana, etc.
    contract_address = Column(String(100), nullable=True)  # Token contract address
    asset_type = Column(String(50), default="crypto")  # crypto, stock, nft, stablecoin
    
    # Holdings
    quantity = Column(Float, default=0.0)
    average_buy_price = Column(Float, default=0.0)  # Average purchase price in USD
    current_price = Column(Float, default=0.0)  # Current price in USD
    
    # Value calculations
    cost_basis = Column(Float, default=0.0)  # quantity * average_buy_price
    current_value = Column(Float, default=0.0)  # quantity * current_price
    unrealized_pnl = Column(Float, default=0.0)  # current_value - cost_basis
    unrealized_pnl_percent = Column(Float, default=0.0)  # (unrealized_pnl / cost_basis) * 100
    
    # Performance
    price_change_24h = Column(Float, default=0.0)
    price_change_percent_24h = Column(Float, default=0.0)
    
    # Metadata
    is_staked = Column(Boolean, default=False)  # Is asset currently staked?
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="assets")
    
    __table_args__ = (
        Index('ix_assets_portfolio_symbol', 'portfolio_id', 'symbol'),
    )
    
    def to_dict(self) -> dict:
        """Convert asset to dictionary."""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "symbol": self.symbol,
            "name": self.name,
            "blockchain": self.blockchain,
            "contract_address": self.contract_address,
            "asset_type": self.asset_type,
            "quantity": round(self.quantity, 6),
            "average_buy_price": round(self.average_buy_price, 2),
            "current_price": round(self.current_price, 2),
            "cost_basis": round(self.cost_basis, 2),
            "current_value": round(self.current_value, 2),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "unrealized_pnl_percent": round(self.unrealized_pnl_percent, 2),
            "price_change_24h": round(self.price_change_24h, 2),
            "price_change_percent_24h": round(self.price_change_percent_24h, 2),
            "is_staked": self.is_staked,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class StakingPosition(Base):
    """Staking position in DeFi protocols."""
    __tablename__ = "staking_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Protocol information
    protocol_name = Column(String(100), nullable=False)  # Lido, Rocket Pool, etc.
    protocol_url = Column(String(255), nullable=True)
    blockchain = Column(String(50), nullable=False)  # Ethereum, Solana, etc.
    
    # Asset details
    staked_asset_symbol = Column(String(20), nullable=False)
    staked_asset_name = Column(String(100), nullable=False)
    staked_amount = Column(Float, default=0.0)
    
    # Rewards
    reward_asset_symbol = Column(String(20), nullable=True)  # stETH, rETH, etc.
    reward_asset_name = Column(String(100), nullable=True)
    pending_rewards = Column(Float, default=0.0)
    total_rewards_earned = Column(Float, default=0.0)
    
    # APY/APR
    apy = Column(Float, default=0.0)  # Annual Percentage Yield
    apr = Column(Float, default=0.0)  # Annual Percentage Rate
    
    # Position value
    staked_value_usd = Column(Float, default=0.0)
    rewards_value_usd = Column(Float, default=0.0)
    total_value_usd = Column(Float, default=0.0)
    
    # Status
    lock_period_days = Column(Integer, nullable=True)  # Lock period in days
    unlock_date = Column(DateTime, nullable=True)  # When position unlocks
    is_locked = Column(Boolean, default=False)  # Is position currently locked?
    
    # Metadata
    position_start_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="staking_positions")
    
    def to_dict(self) -> dict:
        """Convert staking position to dictionary."""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "protocol_name": self.protocol_name,
            "protocol_url": self.protocol_url,
            "blockchain": self.blockchain,
            "staked_asset_symbol": self.staked_asset_symbol,
            "staked_asset_name": self.staked_asset_name,
            "staked_amount": round(self.staked_amount, 6),
            "reward_asset_symbol": self.reward_asset_symbol,
            "reward_asset_name": self.reward_asset_name,
            "pending_rewards": round(self.pending_rewards, 6),
            "total_rewards_earned": round(self.total_rewards_earned, 6),
            "apy": round(self.apy, 2),
            "apr": round(self.apr, 2),
            "staked_value_usd": round(self.staked_value_usd, 2),
            "rewards_value_usd": round(self.rewards_value_usd, 2),
            "total_value_usd": round(self.total_value_usd, 2),
            "lock_period_days": self.lock_period_days,
            "unlock_date": self.unlock_date.isoformat() if self.unlock_date else None,
            "is_locked": self.is_locked,
            "position_start_date": self.position_start_date.isoformat() if self.position_start_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class LiquidityPosition(Base):
    """Liquidity pool position."""
    __tablename__ = "liquidity_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Pool information
    protocol_name = Column(String(100), nullable=False)  # Uniswap, Curve, etc.
    pool_name = Column(String(100), nullable=False)  # ETH/USDT, etc.
    pool_address = Column(String(100), nullable=True)
    blockchain = Column(String(50), nullable=False)
    
    # Assets in pool
    token0_symbol = Column(String(20), nullable=False)
    token0_amount = Column(Float, default=0.0)
    token0_value_usd = Column(Float, default=0.0)
    
    token1_symbol = Column(String(20), nullable=False)
    token1_amount = Column(Float, default=0.0)
    token1_value_usd = Column(Float, default=0.0)
    
    # Position details
    lp_token_amount = Column(Float, default=0.0)  # LP tokens held
    lp_token_value_usd = Column(Float, default=0.0)  # Total value of LP tokens
    share_of_pool = Column(Float, default=0.0)  # % of pool owned
    
    # Rewards
    reward_asset_symbol = Column(String(20), nullable=True)
    pending_rewards = Column(Float, default=0.0)
    total_rewards_earned = Column(Float, default=0.0)
    
    # APY/Impermanent loss
    apy = Column(Float, default=0.0)
    impermanent_loss_percent = Column(Float, default=0.0)  # % impermanent loss
    
    # Metadata
    position_start_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="liquidity_positions")
    
    def to_dict(self) -> dict:
        """Convert liquidity position to dictionary."""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "protocol_name": self.protocol_name,
            "pool_name": self.pool_name,
            "pool_address": self.pool_address,
            "blockchain": self.blockchain,
            "token0_symbol": self.token0_symbol,
            "token0_amount": round(self.token0_amount, 6),
            "token0_value_usd": round(self.token0_value_usd, 2),
            "token1_symbol": self.token1_symbol,
            "token1_amount": round(self.token1_amount, 6),
            "token1_value_usd": round(self.token1_value_usd, 2),
            "lp_token_amount": round(self.lp_token_amount, 6),
            "lp_token_value_usd": round(self.lp_token_value_usd, 2),
            "share_of_pool": round(self.share_of_pool, 4),
            "reward_asset_symbol": self.reward_asset_symbol,
            "pending_rewards": round(self.pending_rewards, 6),
            "total_rewards_earned": round(self.total_rewards_earned, 6),
            "apy": round(self.apy, 2),
            "impermanent_loss_percent": round(self.impermanent_loss_percent, 2),
            "position_start_date": self.position_start_date.isoformat() if self.position_start_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class MarketData(Base):
    """Historical market data for assets."""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Price data
    price_usd = Column(Float, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    
    # Derived metrics
    price_change_24h = Column(Float, default=0.0)
    price_change_percent_24h = Column(Float, default=0.0)
    volume_change_24h = Column(Float, default=0.0)
    
    # Market sentiment
    fear_greed_index = Column(Float, nullable=True)  # 0-100 scale
    social_volume = Column(Float, nullable=True)  # Social media mentions
    
    # Metadata
    source = Column(String(50), default="coingecko")  # coingecko, binance, etc.
    
    __table_args__ = (
        Index('ix_market_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def to_dict(self) -> dict:
        """Convert market data to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "price_usd": round(self.price_usd, 2),
            "open": round(self.open, 2) if self.open else None,
            "high": round(self.high, 2) if self.high else None,
            "low": round(self.low, 2) if self.low else None,
            "close": round(self.close, 2) if self.close else None,
            "volume_24h": round(self.volume_24h, 2) if self.volume_24h else None,
            "market_cap": round(self.market_cap, 2) if self.market_cap else None,
            "price_change_24h": round(self.price_change_24h, 2),
            "price_change_percent_24h": round(self.price_change_percent_24h, 2),
            "volume_change_24h": round(self.volume_change_24h, 2),
            "fear_greed_index": round(self.fear_greed_index, 2) if self.fear_greed_index else None,
            "social_volume": round(self.social_volume, 2) if self.social_volume else None,
            "source": self.source,
        }


class GovernanceProposal(Base):
    """DAO governance proposals."""
    __tablename__ = "governance_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # DAO information
    dao_name = Column(String(100), nullable=False)
    dao_logo = Column(String(255), nullable=True)
    blockchain = Column(String(50), nullable=False)
    
    # Proposal details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    proposal_type = Column(String(50), default="governance")  # governance, treasury, parameter
    status = Column(String(50), default="pending")  # pending, active, passed, rejected, executed
    
    # Voting
    voting_start = Column(DateTime, nullable=True)
    voting_end = Column(DateTime, nullable=True)
    quorum = Column(Float, default=0.0)  # % required
    current_quorum = Column(Float, default=0.0)  # % achieved
    
    # Vote results
    votes_for = Column(Float, default=0.0)
    votes_against = Column(Float, default=0.0)
    votes_abstain = Column(Float, default=0.0)
    total_votes = Column(Float, default=0.0)
    
    # User interaction
    user_vote = Column(String(20), nullable=True)  # for, against, abstain
    user_voting_power = Column(Float, default=0.0)
    
    # Metadata
    creator_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert proposal to dictionary."""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "dao_name": self.dao_name,
            "dao_logo": self.dao_logo,
            "blockchain": self.blockchain,
            "title": self.title,
            "description": self.description,
            "proposal_type": self.proposal_type,
            "status": self.status,
            "voting_start": self.voting_start.isoformat() if self.voting_start else None,
            "voting_end": self.voting_end.isoformat() if self.voting_end else None,
            "quorum": round(self.quorum, 2),
            "current_quorum": round(self.current_quorum, 2),
            "votes_for": round(self.votes_for, 2),
            "votes_against": round(self.votes_against, 2),
            "votes_abstain": round(self.votes_abstain, 2),
            "total_votes": round(self.total_votes, 2),
            "user_vote": self.user_vote,
            "user_voting_power": round(self.user_voting_power, 2),
            "creator_address": self.creator_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Prediction(Base):
    """AI predictions for asset prices."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    model_id = Column(String(100), nullable=False)  # OpenGradient model ID
    model_name = Column(String(100), nullable=False)  # BitQuant, etc.
    
    # Prediction details
    prediction_type = Column(String(50), default="price")  # price, volatility, sentiment
    horizon = Column(String(20), default="24h")  # 1h, 24h, 7d, 30d
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Prediction values
    predicted_price = Column(Float, nullable=True)
    predicted_change = Column(Float, nullable=True)  # % change
    predicted_high = Column(Float, nullable=True)
    predicted_low = Column(Float, nullable=True)
    
    # Confidence metrics
    confidence_score = Column(Float, default=0.0)  # 0-1
    accuracy_score = Column(Float, nullable=True)  # Historical accuracy
    volatility_prediction = Column(Float, nullable=True)
    
    # Risk assessment
    risk_level = Column(String(20), default="medium")  # low, medium, high
    recommendation = Column(String(50), nullable=True)  # buy, hold, sell
    
    # Metadata
    features_used = Column(JSON, nullable=True, default=list)  # Features used for prediction
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_predictions_symbol_horizon', 'symbol', 'horizon'),
    )
    
    def to_dict(self) -> dict:
        """Convert prediction to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "prediction_type": self.prediction_type,
            "horizon": self.horizon,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "predicted_price": round(self.predicted_price, 2) if self.predicted_price else None,
            "predicted_change": round(self.predicted_change, 2) if self.predicted_change else None,
            "predicted_high": round(self.predicted_high, 2) if self.predicted_high else None,
            "predicted_low": round(self.predicted_low, 2) if self.predicted_low else None,
            "confidence_score": round(self.confidence_score, 3),
            "accuracy_score": round(self.accuracy_score, 3) if self.accuracy_score else None,
            "volatility_prediction": round(self.volatility_prediction, 3) if self.volatility_prediction else None,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "features_used": self.features_used or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
