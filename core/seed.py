"""
Seed data for database initialization.
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from models.db_models import MarketData


async def seed_market_data(db: AsyncSession):
    """Seed initial market data for demo purposes."""
    # Check if we already have market data
    result = await db.execute(select(MarketData).limit(1))
    existing = result.scalar_one_or_none()
    
    if existing:
        logger.debug("Market data already exists, skipping seed")
        return
    
    symbols = ["BTC", "ETH", "SOL", "OPG"]
    now = datetime.utcnow()
    
    # Mock price data (realistic values as of 2025)
    mock_prices = {
        "BTC": {"price": 65000.0, "change_24h": 500.0, "change_percent": 0.78, "volume": 25000000000, "market_cap": 1.28e12},
        "ETH": {"price": 3500.0, "change_24h": -25.0, "change_percent": -0.71, "volume": 12000000000, "market_cap": 4.2e11},
        "SOL": {"price": 150.0, "change_24h": 2.5, "change_percent": 1.69, "volume": 3000000000, "market_cap": 6.7e10},
        "OPG": {"price": 0.25, "change_24h": 0.01, "change_percent": 4.17, "volume": 50000000, "market_cap": 2.5e7}
    }
    
    # Create market data entries for each symbol (last 7 days hourly)
    for symbol in symbols:
        mock = mock_prices.get(symbol, {"price": 1.0, "change_24h": 0.0, "change_percent": 0.0, "volume": 0, "market_cap": 0})
        
        # Create 24 hourly data points (last 24 hours)
        for hour_offset in range(24):
            timestamp = now - timedelta(hours=hour_offset)
            
            # Add some random price fluctuation
            price_mult = 1.0 + (hour_offset % 5 - 2) * 0.001  # +/- 0.2%
            price = mock["price"] * price_mult
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=timestamp,
                price_usd=price,
                open=price * 0.995,
                high=price * 1.005,
                low=price * 0.995,
                close=price,
                volume_24h=mock["volume"],
                market_cap=mock["market_cap"],
                price_change_24h=mock["change_24h"],
                price_change_percent_24h=mock["change_percent"],
                volume_change_24h=0.0,
                fear_greed_index=65.0,
                social_volume=1000 + hour_offset * 10,
                source="seed"
            )
            
            db.add(market_data)
    
    await db.commit()
    logger.info(f"Seeded market data for {len(symbols)} symbols")
    
    return True


async def seed_all(db: AsyncSession):
    """Seed all initial data."""
    await seed_market_data(db)