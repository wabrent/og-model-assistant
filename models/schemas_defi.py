"""
Pydantic schemas for DeFi API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============== Portfolio Schemas ==============

class PortfolioBase(BaseModel):
    """Base schema for Portfolio."""
    name: str = Field(default="My Portfolio")
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """Schema for creating a Portfolio."""
    user_id: str  # wallet address


class PortfolioUpdate(BaseModel):
    """Schema for updating a Portfolio."""
    name: Optional[str] = None
    description: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    """Schema for Portfolio response."""
    id: int
    user_id: str
    total_value_usd: float = 0.0
    total_value_change_24h: float = 0.0
    total_value_change_percent_24h: float = 0.0
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    monthly_pnl: float = 0.0
    all_time_pnl: float = 0.0
    volatility_30d: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    asset_distribution: Dict[str, float] = {}
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    asset_count: int = 0
    staking_count: int = 0
    liquidity_count: int = 0
    
    class Config:
        from_attributes = True


# ============== Asset Schemas ==============

class AssetBase(BaseModel):
    """Base schema for Asset."""
    symbol: str
    name: str
    blockchain: Optional[str] = None
    contract_address: Optional[str] = None
    asset_type: str = "crypto"
    quantity: float = 0.0
    average_buy_price: float = 0.0


class AssetCreate(AssetBase):
    """Schema for creating an Asset."""
    portfolio_id: int


class AssetUpdate(BaseModel):
    """Schema for updating an Asset."""
    quantity: Optional[float] = None
    average_buy_price: Optional[float] = None
    current_price: Optional[float] = None


class AssetResponse(AssetBase):
    """Schema for Asset response."""
    id: int
    portfolio_id: int
    current_price: float = 0.0
    cost_basis: float = 0.0
    current_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    price_change_24h: float = 0.0
    price_change_percent_24h: float = 0.0
    is_staked: bool = False
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============== Staking Position Schemas ==============

class StakingPositionBase(BaseModel):
    """Base schema for Staking Position."""
    protocol_name: str
    protocol_url: Optional[str] = None
    blockchain: str
    staked_asset_symbol: str
    staked_asset_name: str
    staked_amount: float = 0.0
    reward_asset_symbol: Optional[str] = None
    reward_asset_name: Optional[str] = None
    lock_period_days: Optional[int] = None
    unlock_date: Optional[datetime] = None


class StakingPositionCreate(StakingPositionBase):
    """Schema for creating a Staking Position."""
    portfolio_id: int


class StakingPositionUpdate(BaseModel):
    """Schema for updating a Staking Position."""
    staked_amount: Optional[float] = None
    pending_rewards: Optional[float] = None
    apy: Optional[float] = None


class StakingPositionResponse(StakingPositionBase):
    """Schema for Staking Position response."""
    id: int
    portfolio_id: int
    pending_rewards: float = 0.0
    total_rewards_earned: float = 0.0
    apy: float = 0.0
    apr: float = 0.0
    staked_value_usd: float = 0.0
    rewards_value_usd: float = 0.0
    total_value_usd: float = 0.0
    is_locked: bool = False
    position_start_date: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============== Liquidity Position Schemas ==============

class LiquidityPositionBase(BaseModel):
    """Base schema for Liquidity Position."""
    protocol_name: str
    pool_name: str
    pool_address: Optional[str] = None
    blockchain: str
    token0_symbol: str
    token0_amount: float = 0.0
    token1_symbol: str
    token1_amount: float = 0.0
    reward_asset_symbol: Optional[str] = None


class LiquidityPositionCreate(LiquidityPositionBase):
    """Schema for creating a Liquidity Position."""
    portfolio_id: int


class LiquidityPositionUpdate(BaseModel):
    """Schema for updating a Liquidity Position."""
    token0_amount: Optional[float] = None
    token1_amount: Optional[float] = None
    pending_rewards: Optional[float] = None


class LiquidityPositionResponse(LiquidityPositionBase):
    """Schema for Liquidity Position response."""
    id: int
    portfolio_id: int
    token0_value_usd: float = 0.0
    token1_value_usd: float = 0.0
    lp_token_amount: float = 0.0
    lp_token_value_usd: float = 0.0
    share_of_pool: float = 0.0
    pending_rewards: float = 0.0
    total_rewards_earned: float = 0.0
    apy: float = 0.0
    impermanent_loss_percent: float = 0.0
    position_start_date: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============== Market Data Schemas ==============

class MarketDataBase(BaseModel):
    """Base schema for Market Data."""
    symbol: str
    timestamp: datetime
    price_usd: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None


class MarketDataResponse(MarketDataBase):
    """Schema for Market Data response."""
    id: int
    price_change_24h: float = 0.0
    price_change_percent_24h: float = 0.0
    volume_change_24h: float = 0.0
    fear_greed_index: Optional[float] = None
    social_volume: Optional[float] = None
    source: str = "coingecko"
    
    class Config:
        from_attributes = True


class MarketDataRequest(BaseModel):
    """Schema for Market Data request."""
    symbols: List[str] = Field(default=["BTC", "ETH", "SOL"])
    timeframe: str = Field(default="24h")  # 1h, 24h, 7d, 30d
    limit: int = Field(default=100, ge=1, le=1000)


# ============== Governance Proposal Schemas ==============

class GovernanceProposalBase(BaseModel):
    """Base schema for Governance Proposal."""
    proposal_id: str
    dao_name: str
    dao_logo: Optional[str] = None
    blockchain: str
    title: str
    description: Optional[str] = None
    proposal_type: str = "governance"


class GovernanceProposalResponse(GovernanceProposalBase):
    """Schema for Governance Proposal response."""
    id: int
    status: str = "pending"
    voting_start: Optional[datetime] = None
    voting_end: Optional[datetime] = None
    quorum: float = 0.0
    current_quorum: float = 0.0
    votes_for: float = 0.0
    votes_against: float = 0.0
    votes_abstain: float = 0.0
    total_votes: float = 0.0
    user_vote: Optional[str] = None
    user_voting_power: float = 0.0
    creator_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Prediction Schemas ==============

class PredictionBase(BaseModel):
    """Base schema for Prediction."""
    symbol: str
    model_id: str
    model_name: str
    prediction_type: str = "price"
    horizon: str = "24h"
    timestamp: datetime


class PredictionResponse(PredictionBase):
    """Schema for Prediction response."""
    id: int
    predicted_price: Optional[float] = None
    predicted_change: Optional[float] = None
    predicted_high: Optional[float] = None
    predicted_low: Optional[float] = None
    confidence_score: float = 0.0
    accuracy_score: Optional[float] = None
    volatility_prediction: Optional[float] = None
    risk_level: str = "medium"
    recommendation: Optional[str] = None
    features_used: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    """Schema for Prediction request."""
    symbol: str
    horizon: str = Field(default="24h", pattern="^(1h|24h|7d|30d)$")
    model_name: Optional[str] = "BitQuant"


# ============== DeFi Analytics Schemas ==============

class PortfolioAnalyticsResponse(BaseModel):
    """Schema for Portfolio Analytics response."""
    portfolio_id: int
    total_value_usd: float
    daily_change_usd: float
    daily_change_percent: float
    top_assets: List[Dict[str, Any]]
    asset_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]


class MarketAnalyticsResponse(BaseModel):
    """Schema for Market Analytics response."""
    timestamp: datetime
    total_market_cap: float
    market_cap_change_24h: float
    fear_greed_index: Optional[float]
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    trending_assets: List[Dict[str, Any]]


# ============== WebSocket Schemas ==============

class PriceUpdate(BaseModel):
    """Schema for WebSocket price updates."""
    symbol: str
    price_usd: float
    price_change_24h: float
    price_change_percent_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime


class PortfolioUpdate(BaseModel):
    """Schema for WebSocket portfolio updates."""
    portfolio_id: int
    total_value_usd: float
    daily_pnl: float
    timestamp: datetime


# ============== AI Assistant Schemas ==============

class DeFiQueryRequest(BaseModel):
    """Schema for DeFi AI assistant query."""
    query: str
    portfolio_id: Optional[int] = None
    context: Dict[str, Any] = {}


class DeFiQueryResponse(BaseModel):
    """Schema for DeFi AI assistant response."""
    answer: str
    recommendations: List[str] = []
    data_points: Dict[str, Any] = {}
    confidence: float = 0.0