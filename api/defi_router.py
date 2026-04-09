"""
API Router for DeFi operations - portfolio management, market data, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from loguru import logger

from core.database import get_db
from core.cache import cache
from models.schemas_defi import (
    PortfolioCreate, PortfolioUpdate, PortfolioResponse,
    AssetCreate, AssetUpdate, AssetResponse,
    StakingPositionCreate, StakingPositionUpdate, StakingPositionResponse,
    LiquidityPositionCreate, LiquidityPositionUpdate, LiquidityPositionResponse,
    MarketDataRequest, MarketDataResponse,
    GovernanceProposalResponse, PredictionResponse, PredictionRequest,
    PortfolioAnalyticsResponse, MarketAnalyticsResponse,
    DeFiQueryRequest, DeFiQueryResponse
)
from services.defi_service import defi_service
from services.chat_service import chat_service

router = APIRouter(prefix="/api/defi", tags=["DeFi"])


# ============== Portfolio Endpoints ==============

@router.get("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    user_id: Optional[str] = Query(None, description="User ID (wallet address) for ownership verification"),
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio by ID."""
    portfolio = await defi_service.get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return portfolio


@router.get("/portfolio/user/{user_id}", response_model=PortfolioResponse)
async def get_user_portfolio(
    user_id: str,
    create_if_not_exists: bool = Query(False, description="Create portfolio if it doesn't exist"),
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio by user ID (wallet address)."""
    portfolio = await defi_service.get_user_portfolio(db, user_id)
    
    if not portfolio and create_if_not_exists:
        # Create default portfolio
        portfolio_data = PortfolioCreate(
            user_id=user_id,
            name=f"{user_id[:8]}... Portfolio",
            description="Default portfolio"
        )
        portfolio = await defi_service.create_portfolio(db, portfolio_data)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return portfolio


@router.post("/portfolio", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new portfolio."""
    portfolio = await defi_service.create_portfolio(db, portfolio_data)
    return portfolio


@router.put("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    update_data: PortfolioUpdate,
    user_id: Optional[str] = Query(None, description="User ID for ownership verification"),
    db: AsyncSession = Depends(get_db)
):
    """Update portfolio information."""
    portfolio = await defi_service.update_portfolio(db, portfolio_id, update_data, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return portfolio


@router.delete("/portfolio/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    user_id: Optional[str] = Query(None, description="User ID for ownership verification"),
    db: AsyncSession = Depends(get_db)
):
    """Delete portfolio."""
    success = await defi_service.delete_portfolio(db, portfolio_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return {"message": "Portfolio deleted successfully"}


# ============== Asset Endpoints ==============

@router.get("/portfolio/{portfolio_id}/assets", response_model=List[AssetResponse])
async def get_portfolio_assets(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all assets in a portfolio."""
    assets = await defi_service.get_portfolio_assets(db, portfolio_id)
    return assets


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    portfolio_id: Optional[int] = Query(None, description="Optional portfolio ID for verification"),
    db: AsyncSession = Depends(get_db)
):
    """Get asset by ID."""
    asset = await defi_service.get_asset(db, asset_id, portfolio_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.post("/assets", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new asset in a portfolio."""
    try:
        asset = await defi_service.create_asset(db, asset_data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    update_data: AssetUpdate,
    portfolio_id: Optional[int] = Query(None, description="Optional portfolio ID for verification"),
    db: AsyncSession = Depends(get_db)
):
    """Update asset information."""
    asset = await defi_service.update_asset(db, asset_id, update_data, portfolio_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: int,
    portfolio_id: Optional[int] = Query(None, description="Optional portfolio ID for verification"),
    db: AsyncSession = Depends(get_db)
):
    """Delete asset from portfolio."""
    success = await defi_service.delete_asset(db, asset_id, portfolio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {"message": "Asset deleted successfully"}


# ============== Market Data Endpoints ==============

@router.get("/market/current", response_model=Dict[str, Dict[str, Any]])
async def get_current_prices(
    symbols: List[str] = Query(["BTC", "ETH", "SOL"], description="List of symbols to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """Get current prices for multiple symbols."""
    # Try cache first
    cache_key = f"market:prices:{':'.join(sorted(symbols))}"
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    prices = await defi_service.get_current_prices(db, symbols)
    
    # Cache for 60 seconds
    await cache.set(cache_key, json.dumps(prices, default=str), expire=60)
    
    return prices


@router.post("/market/historical", response_model=List[MarketDataResponse])
async def get_historical_market_data(
    request: MarketDataRequest,
    db: AsyncSession = Depends(get_db)
):
    """Get historical market data for symbols."""
    all_data = []
    for symbol in request.symbols:
        data = await defi_service.get_market_data(
            db, symbol, request.timeframe, request.limit
        )
        all_data.extend(data)
    
    return all_data


@router.post("/market/update/{symbol}")
async def update_market_price(
    symbol: str,
    price_usd: float = Query(..., description="Current price in USD"),
    price_change_24h: float = Query(0.0, description="24h price change in USD"),
    price_change_percent_24h: float = Query(0.0, description="24h price change percentage"),
    db: AsyncSession = Depends(get_db)
):
    """Update market price for a symbol (admin/background job)."""
    updated_count = await defi_service.update_asset_prices(
        db, symbol, price_usd, price_change_24h, price_change_percent_24h
    )
    
    # Save market data point
    await defi_service.save_market_data(
        db, symbol, price_usd, datetime.utcnow(),
        price_change_24h=price_change_24h,
        price_change_percent_24h=price_change_percent_24h
    )
    
    return {
        "message": f"Updated {updated_count} assets with new price",
        "symbol": symbol,
        "price_usd": price_usd
    }


# ============== Analytics Endpoints ==============

@router.get("/portfolio/{portfolio_id}/analytics", response_model=PortfolioAnalyticsResponse)
async def get_portfolio_analytics(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive portfolio analytics."""
    analytics = await defi_service.get_portfolio_analytics(db, portfolio_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return analytics


@router.get("/market/analytics", response_model=MarketAnalyticsResponse)
async def get_market_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Get overall market analytics."""
    analytics = await defi_service.get_market_analytics(db)
    return analytics


# ============== AI Prediction Endpoints ==============

@router.get("/predictions/{symbol}", response_model=List[PredictionResponse])
async def get_predictions(
    symbol: str,
    horizon: str = Query("24h", pattern="^(1h|24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get AI predictions for a symbol."""
    predictions = await defi_service.get_predictions(db, symbol, horizon)
    return predictions


@router.post("/predictions")
async def create_prediction(
    symbol: str,
    model_id: str = Query(..., description="OpenGradient model ID"),
    model_name: str = Query("BitQuant", description="Model name"),
    predicted_price: Optional[float] = Query(None),
    predicted_change: Optional[float] = Query(None),
    confidence_score: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db)
):
    """Save AI prediction (for ML models)."""
    prediction = await defi_service.save_prediction(
        db, symbol, model_id, model_name,
        predicted_price, predicted_change, confidence_score
    )
    
    return prediction


# ============== DeFi AI Assistant Endpoints ==============

@router.post("/assistant/query", response_model=DeFiQueryResponse)
async def defi_assistant_query(
    query_request: DeFiQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Query DeFi AI assistant about portfolio, market, or strategies."""
    # Build context from portfolio if provided
    context = query_request.context.copy()
    
    if query_request.portfolio_id:
        portfolio = await defi_service.get_portfolio(db, query_request.portfolio_id)
        if portfolio:
            portfolio_data = portfolio.to_dict()
            assets = await defi_service.get_portfolio_assets(db, query_request.portfolio_id)
            portfolio_data["assets"] = [asset.to_dict() for asset in assets]
            context["portfolio"] = portfolio_data
    
    # Add market context
    market_analytics = await defi_service.get_market_analytics(db)
    context["market"] = market_analytics
    
    # Build system prompt for DeFi
    system_prompt = f"""You are a DeFi AI assistant specialized in cryptocurrency portfolio management, market analysis, and trading strategies.

CONTEXT:
Portfolio: {context.get('portfolio', 'No portfolio data')}
Market: {context.get('market', 'No market data')}

Provide accurate, helpful advice about DeFi, portfolio management, market trends, and cryptocurrency investments.
Focus on risk management, diversification, and data-driven insights.
If asked about specific assets, provide current market information and analysis.
If asked about portfolio optimization, suggest strategies based on modern portfolio theory.
Always mention risks and recommend doing your own research (DYOR)."""
    
    # Use chat service with DeFi context
    try:
        response = await chat_service.process_message(
            db, query_request.query, "defi_assistant", system_prompt
        )
        
        # Parse response for recommendations
        recommendations = []
        if "recommend" in response.lower() or "suggest" in response.lower():
            recommendations = [
                "Consider diversifying your portfolio across different asset classes",
                "Review your risk tolerance and adjust position sizes accordingly",
                "Set stop-loss orders to manage downside risk",
                "Regularly rebalance your portfolio based on market conditions"
            ]
        
        return DeFiQueryResponse(
            answer=response,
            recommendations=recommendations,
            data_points=context,
            confidence=0.85  # Placeholder confidence score
        )
    except Exception as e:
        logger.error(f"DeFi assistant error: {e}")
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")


# ============== WebSocket Endpoints ==============

# Active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {
    "prices": [],
    "portfolio": []
}


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket for real-time price updates."""
    await websocket.accept()
    active_connections["prices"].append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections["prices"].remove(websocket)


@router.websocket("/ws/portfolio/{portfolio_id}")
async def websocket_portfolio(websocket: WebSocket, portfolio_id: int):
    """WebSocket for portfolio updates."""
    await websocket.accept()
    
    if "portfolio" not in active_connections:
        active_connections["portfolio"] = []
    
    active_connections["portfolio"].append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections["portfolio"].remove(websocket)


# Background task to broadcast updates (would be called by external price feeds)
async def broadcast_price_update(symbol: str, price_data: Dict[str, Any]):
    """Broadcast price update to all connected clients."""
    message = {
        "type": "price_update",
        "symbol": symbol,
        "data": price_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    for connection in active_connections["prices"]:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send price update: {e}")


async def broadcast_portfolio_update(portfolio_id: int, portfolio_data: Dict[str, Any]):
    """Broadcast portfolio update to all connected clients."""
    message = {
        "type": "portfolio_update",
        "portfolio_id": portfolio_id,
        "data": portfolio_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    for connection in active_connections["portfolio"]:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send portfolio update: {e}")


# ============== Utility Endpoints ==============

@router.get("/health")
async def defi_health():
    """DeFi module health check."""
    return {
        "status": "healthy",
        "module": "defi",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "portfolio_management",
            "asset_tracking",
            "market_data",
            "analytics",
            "ai_predictions",
            "websocket_updates",
            "defi_assistant"
        ]
    }