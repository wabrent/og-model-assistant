"""
DeFi service for portfolio management, market data, and analytics.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func, or_, and_, desc, asc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from models.db_models import (
    Portfolio, Asset, StakingPosition, LiquidityPosition,
    MarketData, GovernanceProposal, Prediction, UserToken
)
from models.schemas_defi import (
    PortfolioCreate, PortfolioUpdate, AssetCreate, AssetUpdate,
    StakingPositionCreate, StakingPositionUpdate,
    LiquidityPositionCreate, LiquidityPositionUpdate,
    MarketDataRequest, PredictionRequest
)


class DeFiService:
    """Service for DeFi operations."""
    
    # ============== Portfolio Operations ==============
    
    async def get_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int,
        user_id: Optional[str] = None
    ) -> Optional[Portfolio]:
        """Get portfolio by ID with optional user ownership check."""
        query = select(Portfolio).where(Portfolio.id == portfolio_id)
        
        if user_id:
            query = query.where(Portfolio.user_id == user_id)
            
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_portfolio(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[Portfolio]:
        """Get portfolio by user ID (wallet address)."""
        query = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_portfolio(
        self,
        db: AsyncSession,
        portfolio_data: PortfolioCreate
    ) -> Portfolio:
        """Create a new portfolio for a user."""
        # Check if portfolio already exists for user
        existing = await self.get_user_portfolio(db, portfolio_data.user_id)
        if existing:
            return existing
        
        portfolio = Portfolio(
            user_id=portfolio_data.user_id,
            name=portfolio_data.name,
            description=portfolio_data.description
        )
        
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        
        logger.info(f"Created portfolio {portfolio.id} for user {portfolio_data.user_id}")
        return portfolio
    
    async def update_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int,
        update_data: PortfolioUpdate,
        user_id: Optional[str] = None
    ) -> Optional[Portfolio]:
        """Update portfolio information."""
        portfolio = await self.get_portfolio(db, portfolio_id, user_id)
        if not portfolio:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(portfolio, key, value)
        
        portfolio.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(portfolio)
        
        return portfolio
    
    async def delete_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete portfolio and all associated assets."""
        portfolio = await self.get_portfolio(db, portfolio_id, user_id)
        if not portfolio:
            return False
        
        await db.delete(portfolio)
        await db.commit()
        
        logger.info(f"Deleted portfolio {portfolio_id}")
        return True
    
    async def calculate_portfolio_metrics(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> Dict[str, Any]:
        """Calculate portfolio metrics (value, P&L, risk)."""
        portfolio = await self.get_portfolio(db, portfolio_id)
        if not portfolio:
            return {}
        
        # Get all assets
        assets_query = select(Asset).where(Asset.portfolio_id == portfolio_id)
        assets_result = await db.execute(assets_query)
        assets = assets_result.scalars().all()
        
        # Calculate total value
        total_value = sum(asset.current_value for asset in assets)
        
        # Calculate P&L
        total_cost_basis = sum(asset.cost_basis for asset in assets)
        total_pnl = total_value - total_cost_basis
        
        # Update portfolio
        portfolio.total_value_usd = total_value
        portfolio.all_time_pnl = total_pnl
        portfolio.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "total_value_usd": total_value,
            "total_cost_basis": total_cost_basis,
            "total_pnl": total_pnl,
            "pnl_percent": (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0,
            "asset_count": len(assets)
        }
    
    # ============== Asset Operations ==============
    
    async def get_asset(
        self,
        db: AsyncSession,
        asset_id: int,
        portfolio_id: Optional[int] = None
    ) -> Optional[Asset]:
        """Get asset by ID with optional portfolio check."""
        query = select(Asset).where(Asset.id == asset_id)
        
        if portfolio_id:
            query = query.where(Asset.portfolio_id == portfolio_id)
            
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_portfolio_assets(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> List[Asset]:
        """Get all assets in a portfolio."""
        query = select(Asset).where(Asset.portfolio_id == portfolio_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_asset(
        self,
        db: AsyncSession,
        asset_data: AssetCreate
    ) -> Asset:
        """Create a new asset in a portfolio."""
        # Check if portfolio exists
        portfolio = await self.get_portfolio(db, asset_data.portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {asset_data.portfolio_id} not found")
        
        # Check if asset already exists in portfolio
        existing_query = select(Asset).where(
            (Asset.portfolio_id == asset_data.portfolio_id) &
            (Asset.symbol == asset_data.symbol)
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # Update existing asset
            existing.quantity += asset_data.quantity
            existing.average_buy_price = (
                (existing.average_buy_price * existing.quantity + 
                 asset_data.average_buy_price * asset_data.quantity) /
                (existing.quantity + asset_data.quantity)
            )
            existing.cost_basis = existing.quantity * existing.average_buy_price
            existing.last_updated = datetime.utcnow()
            
            await db.commit()
            await db.refresh(existing)
            
            # Recalculate portfolio metrics
            await self.calculate_portfolio_metrics(db, asset_data.portfolio_id)
            
            return existing
        
        # Create new asset
        asset = Asset(
            portfolio_id=asset_data.portfolio_id,
            symbol=asset_data.symbol,
            name=asset_data.name,
            blockchain=asset_data.blockchain,
            contract_address=asset_data.contract_address,
            asset_type=asset_data.asset_type,
            quantity=asset_data.quantity,
            average_buy_price=asset_data.average_buy_price,
            cost_basis=asset_data.quantity * asset_data.average_buy_price,
            current_price=asset_data.average_buy_price,  # Initial price = buy price
            current_value=asset_data.quantity * asset_data.average_buy_price,
            last_updated=datetime.utcnow()
        )
        
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        
        # Recalculate portfolio metrics
        await self.calculate_portfolio_metrics(db, asset_data.portfolio_id)
        
        logger.info(f"Created asset {asset.symbol} in portfolio {asset_data.portfolio_id}")
        return asset
    
    async def update_asset(
        self,
        db: AsyncSession,
        asset_id: int,
        update_data: AssetUpdate,
        portfolio_id: Optional[int] = None
    ) -> Optional[Asset]:
        """Update asset information."""
        asset = await self.get_asset(db, asset_id, portfolio_id)
        if not asset:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(asset, key, value)
        
        # Recalculate derived values
        if 'quantity' in update_dict or 'average_buy_price' in update_dict:
            asset.cost_basis = asset.quantity * asset.average_buy_price
        
        if 'current_price' in update_dict or 'quantity' in update_dict:
            asset.current_value = asset.quantity * asset.current_price
        
        if asset.cost_basis > 0:
            asset.unrealized_pnl = asset.current_value - asset.cost_basis
            asset.unrealized_pnl_percent = (asset.unrealized_pnl / asset.cost_basis) * 100
        
        asset.last_updated = datetime.utcnow()
        
        await db.commit()
        await db.refresh(asset)
        
        # Recalculate portfolio metrics
        await self.calculate_portfolio_metrics(db, asset.portfolio_id)
        
        return asset
    
    async def delete_asset(
        self,
        db: AsyncSession,
        asset_id: int,
        portfolio_id: Optional[int] = None
    ) -> bool:
        """Delete asset from portfolio."""
        asset = await self.get_asset(db, asset_id, portfolio_id)
        if not asset:
            return False
        
        portfolio_id = asset.portfolio_id
        await db.delete(asset)
        await db.commit()
        
        # Recalculate portfolio metrics
        await self.calculate_portfolio_metrics(db, portfolio_id)
        
        logger.info(f"Deleted asset {asset_id} from portfolio {portfolio_id}")
        return True
    
    async def update_asset_prices(
        self,
        db: AsyncSession,
        symbol: str,
        price_usd: float,
        price_change_24h: float = 0.0,
        price_change_percent_24h: float = 0.0
    ) -> int:
        """Update price for all assets with given symbol."""
        # Find all assets with this symbol
        query = select(Asset).where(Asset.symbol == symbol)
        result = await db.execute(query)
        assets = result.scalars().all()
        
        updated_count = 0
        for asset in assets:
            asset.current_price = price_usd
            asset.price_change_24h = price_change_24h
            asset.price_change_percent_24h = price_change_percent_24h
            asset.current_value = asset.quantity * price_usd
            
            if asset.cost_basis > 0:
                asset.unrealized_pnl = asset.current_value - asset.cost_basis
                asset.unrealized_pnl_percent = (asset.unrealized_pnl / asset.cost_basis) * 100
            
            asset.last_updated = datetime.utcnow()
            updated_count += 1
            
            # Recalculate portfolio metrics
            await self.calculate_portfolio_metrics(db, asset.portfolio_id)
        
        if updated_count > 0:
            await db.commit()
        
        return updated_count
    
    # ============== Market Data Operations ==============
    
    async def get_market_data(
        self,
        db: AsyncSession,
        symbol: str,
        timeframe: str = "24h",
        limit: int = 100
    ) -> List[MarketData]:
        """Get historical market data for a symbol."""
        # Calculate time range based on timeframe
        now = datetime.utcnow()
        if timeframe == "1h":
            start_time = now - timedelta(hours=1)
        elif timeframe == "24h":
            start_time = now - timedelta(days=1)
        elif timeframe == "7d":
            start_time = now - timedelta(days=7)
        elif timeframe == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        query = (
            select(MarketData)
            .where(MarketData.symbol == symbol)
            .where(MarketData.timestamp >= start_time)
            .order_by(desc(MarketData.timestamp))
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def save_market_data(
        self,
        db: AsyncSession,
        symbol: str,
        price_usd: float,
        timestamp: datetime,
        **kwargs
    ) -> MarketData:
        """Save market data point."""
        market_data = MarketData(
            symbol=symbol,
            timestamp=timestamp,
            price_usd=price_usd,
            open=kwargs.get('open'),
            high=kwargs.get('high'),
            low=kwargs.get('low'),
            close=kwargs.get('close'),
            volume_24h=kwargs.get('volume_24h'),
            market_cap=kwargs.get('market_cap'),
            price_change_24h=kwargs.get('price_change_24h', 0.0),
            price_change_percent_24h=kwargs.get('price_change_percent_24h', 0.0),
            volume_change_24h=kwargs.get('volume_change_24h', 0.0),
            fear_greed_index=kwargs.get('fear_greed_index'),
            social_volume=kwargs.get('social_volume'),
            source=kwargs.get('source', 'coingecko')
        )
        
        db.add(market_data)
        await db.commit()
        await db.refresh(market_data)
        
        # Update asset prices
        await self.update_asset_prices(
            db, symbol, price_usd,
            kwargs.get('price_change_24h', 0.0),
            kwargs.get('price_change_percent_24h', 0.0)
        )
        
        return market_data
    
    async def get_current_prices(
        self,
        db: AsyncSession,
        symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Get current prices for multiple symbols."""
        result = {}
        
        for symbol in symbols:
            # Get latest market data for symbol
            query = (
                select(MarketData)
                .where(MarketData.symbol == symbol)
                .order_by(desc(MarketData.timestamp))
                .limit(1)
            )
            
            market_result = await db.execute(query)
            market_data = market_result.scalar_one_or_none()
            
            if market_data:
                result[symbol] = {
                    "price_usd": market_data.price_usd,
                    "price_change_24h": market_data.price_change_24h,
                    "price_change_percent_24h": market_data.price_change_percent_24h,
                    "volume_24h": market_data.volume_24h,
                    "market_cap": market_data.market_cap,
                    "timestamp": market_data.timestamp
                }
            else:
                # Fallback to default values
                result[symbol] = {
                    "price_usd": 0.0,
                    "price_change_24h": 0.0,
                    "price_change_percent_24h": 0.0,
                    "volume_24h": 0.0,
                    "market_cap": 0.0,
                    "timestamp": datetime.utcnow()
                }
        
        return result
    
    # ============== Analytics Operations ==============
    
    async def get_portfolio_analytics(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics."""
        portfolio = await self.get_portfolio(db, portfolio_id)
        if not portfolio:
            return {}
        
        assets = await self.get_portfolio_assets(db, portfolio_id)
        
        # Calculate asset allocation
        asset_allocation = {}
        for asset in assets:
            if asset.current_value > 0:
                allocation = (asset.current_value / portfolio.total_value_usd) * 100
                asset_allocation[asset.symbol] = round(allocation, 2)
        
        # Get top 5 assets by value
        top_assets = sorted(assets, key=lambda x: x.current_value, reverse=True)[:5]
        top_assets_data = [
            {
                "symbol": asset.symbol,
                "name": asset.name,
                "value_usd": round(asset.current_value, 2),
                "allocation_percent": round((asset.current_value / portfolio.total_value_usd) * 100, 2),
                "pnl_percent": round(asset.unrealized_pnl_percent, 2)
            }
            for asset in top_assets
        ]
        
        # Calculate risk metrics (simplified)
        total_volatility = sum(
            abs(asset.price_change_percent_24h) * (asset.current_value / portfolio.total_value_usd)
            for asset in assets if portfolio.total_value_usd > 0
        )
        
        return {
            "portfolio_id": portfolio_id,
            "total_value_usd": round(portfolio.total_value_usd, 2),
            "daily_change_usd": round(portfolio.total_value_change_24h, 2),
            "daily_change_percent": round(portfolio.total_value_change_percent_24h, 2),
            "top_assets": top_assets_data,
            "asset_allocation": asset_allocation,
            "risk_metrics": {
                "volatility_30d": round(portfolio.volatility_30d, 2),
                "sharpe_ratio": round(portfolio.sharpe_ratio, 2),
                "max_drawdown": round(portfolio.max_drawdown, 2),
                "daily_volatility": round(total_volatility, 2)
            },
            "performance_metrics": {
                "daily_pnl": round(portfolio.daily_pnl, 2),
                "weekly_pnl": round(portfolio.weekly_pnl, 2),
                "monthly_pnl": round(portfolio.monthly_pnl, 2),
                "all_time_pnl": round(portfolio.all_time_pnl, 2)
            }
        }
    
    async def get_market_analytics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get overall market analytics."""
        # Get latest market data for top symbols
        top_symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT"]
        
        current_prices = await self.get_current_prices(db, top_symbols)
        
        # Calculate total market cap
        total_market_cap = sum(
            data["market_cap"] for data in current_prices.values() 
            if data["market_cap"] is not None
        )
        
        # Find top gainers and losers
        gainers_losers = []
        for symbol, data in current_prices.items():
            if data["price_change_percent_24h"] is not None:
                gainers_losers.append({
                    "symbol": symbol,
                    "price_change_percent_24h": data["price_change_percent_24h"],
                    "price_usd": data["price_usd"]
                })
        
        top_gainers = sorted(gainers_losers, key=lambda x: x["price_change_percent_24h"], reverse=True)[:5]
        top_losers = sorted(gainers_losers, key=lambda x: x["price_change_percent_24h"])[:5]
        
        return {
            "timestamp": datetime.utcnow(),
            "total_market_cap": round(total_market_cap, 2),
            "market_cap_change_24h": 0.0,  # Would need historical data
            "fear_greed_index": None,  # Would need external API
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "trending_assets": top_gainers[:3]  # Top 3 gainers as trending
        }
    
    # ============== AI Prediction Operations ==============
    
    async def get_predictions(
        self,
        db: AsyncSession,
        symbol: str,
        horizon: str = "24h"
    ) -> List[Prediction]:
        """Get predictions for a symbol."""
        query = (
            select(Prediction)
            .where(Prediction.symbol == symbol)
            .where(Prediction.horizon == horizon)
            .order_by(desc(Prediction.timestamp))
            .limit(10)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def save_prediction(
        self,
        db: AsyncSession,
        symbol: str,
        model_id: str,
        model_name: str,
        predicted_price: Optional[float] = None,
        predicted_change: Optional[float] = None,
        confidence_score: float = 0.0,
        **kwargs
    ) -> Prediction:
        """Save AI prediction."""
        prediction = Prediction(
            symbol=symbol,
            model_id=model_id,
            model_name=model_name,
            prediction_type=kwargs.get('prediction_type', 'price'),
            horizon=kwargs.get('horizon', '24h'),
            timestamp=kwargs.get('timestamp', datetime.utcnow()),
            predicted_price=predicted_price,
            predicted_change=predicted_change,
            predicted_high=kwargs.get('predicted_high'),
            predicted_low=kwargs.get('predicted_low'),
            confidence_score=confidence_score,
            accuracy_score=kwargs.get('accuracy_score'),
            volatility_prediction=kwargs.get('volatility_prediction'),
            risk_level=kwargs.get('risk_level', 'medium'),
            recommendation=kwargs.get('recommendation'),
            features_used=kwargs.get('features_used', [])
        )
        
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        
        logger.info(f"Saved prediction for {symbol} by {model_name}")
        return prediction


# Create singleton instance
defi_service = DeFiService()