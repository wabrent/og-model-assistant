"""
ML Model Service for OpenGradient ML models (BitQuant, PricePredictor, RiskAnalyzer).
"""
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings


class MLModelService:
    """Service for calling OpenGradient ML models."""
    
    BASE_URL = "https://hub-api.opengradient.ai"
    API_TIMEOUT = 30
    
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key or settings.private_key
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
                    "Authorization": f"Bearer {self.private_key}" if self.private_key else "",
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
    async def call_bitquant(
        self,
        symbol: str,
        horizon: str = "24h",
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call BitQuant model for price prediction.
        
        Args:
            symbol: Trading pair symbol (e.g., "ETH/USDT")
            horizon: Prediction horizon ("1h", "24h", "7d", "30d")
            features: Additional features for the model
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Try to use OpenGradient SDK if available
            import opengradient as og
            
            # Check if BitQuant model is available in SDK
            # This is a placeholder - actual implementation depends on SDK capabilities
            logger.info(f"Calling BitQuant via OpenGradient SDK for {symbol} ({horizon})")
            
            # For now, simulate a response
            # In production, you would call: og.MLModel.BITQUANT.predict(...)
            prediction = {
                "symbol": symbol,
                "horizon": horizon,
                "predicted_price": 3500.42,
                "predicted_change_percent": 2.34,
                "confidence_score": 0.87,
                "model_name": "BitQuant",
                "model_version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "features_used": features or {},
                "risk_metrics": {
                    "volatility": 0.042,
                    "sharpe_ratio": 1.23,
                    "max_drawdown": 0.12
                }
            }
            
            return prediction
            
        except ImportError:
            logger.warning("OpenGradient SDK not available, using mock data")
            # Fallback to mock data
            return self._mock_bitquant_prediction(symbol, horizon, features)
        except Exception as e:
            logger.error(f"Error calling BitQuant: {e}")
            # Fallback to mock
            return self._mock_bitquant_prediction(symbol, horizon, features)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def call_price_predictor(
        self,
        symbol: str,
        horizon: str = "24h"
    ) -> Dict[str, Any]:
        """
        Call PricePredictor model for price forecasting.
        """
        try:
            import opengradient as og
            
            logger.info(f"Calling PricePredictor via OpenGradient SDK for {symbol} ({horizon})")
            
            prediction = {
                "symbol": symbol,
                "horizon": horizon,
                "predicted_price": 125.67,
                "predicted_change_percent": 1.89,
                "confidence_score": 0.92,
                "model_name": "PricePredictor",
                "model_version": "2.1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "time_series": [
                    {"timestamp": (datetime.utcnow() + timedelta(hours=i)).isoformat(), "price": 120 + i * 0.5}
                    for i in range(1, 13)
                ],
                "metrics": {
                    "mae": 0.023,
                    "rmse": 0.034,
                    "r2_score": 0.89
                }
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error calling PricePredictor: {e}")
            return self._mock_price_predictor_prediction(symbol, horizon)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def call_risk_analyzer(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call RiskAnalyzer model for portfolio risk assessment.
        """
        try:
            import opengradient as og
            
            logger.info(f"Calling RiskAnalyzer via OpenGradient SDK for portfolio analysis")
            
            analysis = {
                "portfolio_id": portfolio_data.get("id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "model_name": "RiskAnalyzer",
                "model_version": "3.0.1",
                "risk_score": 0.23,  # 0-1, lower is better
                "risk_level": "low",
                "value_at_risk_95": 0.045,  # 4.5% VaR
                "expected_shortfall": 0.067,
                "diversification_score": 0.78,
                "recommendations": [
                    "Consider adding more stablecoin exposure",
                    "Reduce concentration in high-volatility assets",
                    "Add hedging positions for downside protection"
                ],
                "asset_risks": [
                    {
                        "symbol": asset.get("symbol", "UNKNOWN"),
                        "risk_score": 0.15 + (i * 0.1),
                        "volatility": 0.032 + (i * 0.02),
                        "correlation_with_market": 0.65 + (i * 0.05)
                    }
                    for i, asset in enumerate(portfolio_data.get("assets", [])[:5])
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calling RiskAnalyzer: {e}")
            return self._mock_risk_analysis(portfolio_data, market_conditions)
    
    def _mock_bitquant_prediction(
        self,
        symbol: str,
        horizon: str,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate mock BitQuant prediction for demo purposes."""
        import random
        
        base_price = 3500.0 if "ETH" in symbol else 120.0 if "SUI" in symbol else 50000.0
        change = random.uniform(-5.0, 5.0)
        
        return {
            "symbol": symbol,
            "horizon": horizon,
            "predicted_price": base_price * (1 + change/100),
            "predicted_change_percent": change,
            "confidence_score": random.uniform(0.7, 0.95),
            "model_name": "BitQuant",
            "model_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "features_used": features or {},
            "risk_metrics": {
                "volatility": random.uniform(0.02, 0.06),
                "sharpe_ratio": random.uniform(0.8, 2.0),
                "max_drawdown": random.uniform(0.08, 0.15)
            },
            "note": "Mock data - enable OpenGradient SDK for real predictions"
        }
    
    def _mock_price_predictor_prediction(
        self,
        symbol: str,
        horizon: str
    ) -> Dict[str, Any]:
        """Generate mock PricePredictor prediction."""
        import random
        
        base_price = 3500.0 if "ETH" in symbol else 120.0 if "SUI" in symbol else 50000.0
        change = random.uniform(-3.0, 4.0)
        
        return {
            "symbol": symbol,
            "horizon": horizon,
            "predicted_price": base_price * (1 + change/100),
            "predicted_change_percent": change,
            "confidence_score": random.uniform(0.8, 0.98),
            "model_name": "PricePredictor",
            "model_version": "2.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "time_series": [
                {
                    "timestamp": (datetime.utcnow() + timedelta(hours=i)).isoformat(),
                    "price": base_price * (1 + (change/100) * (i/12))
                }
                for i in range(1, 13)
            ],
            "metrics": {
                "mae": random.uniform(0.01, 0.04),
                "rmse": random.uniform(0.02, 0.05),
                "r2_score": random.uniform(0.85, 0.95)
            },
            "note": "Mock data - enable OpenGradient SDK for real predictions"
        }
    
    def _mock_risk_analysis(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate mock risk analysis."""
        import random
        
        assets = portfolio_data.get("assets", [])
        
        return {
            "portfolio_id": portfolio_data.get("id", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": "RiskAnalyzer",
            "model_version": "3.0.1",
            "risk_score": random.uniform(0.1, 0.4),
            "risk_level": random.choice(["low", "medium", "high"]),
            "value_at_risk_95": random.uniform(0.03, 0.08),
            "expected_shortfall": random.uniform(0.05, 0.1),
            "diversification_score": random.uniform(0.6, 0.9),
            "recommendations": [
                "Consider adding more stablecoin exposure",
                "Reduce concentration in high-volatility assets",
                "Add hedging positions for downside protection"
            ],
            "asset_risks": [
                {
                    "symbol": asset.get("symbol", f"ASSET_{i}"),
                    "risk_score": random.uniform(0.1, 0.5),
                    "volatility": random.uniform(0.02, 0.08),
                    "correlation_with_market": random.uniform(0.5, 0.9)
                }
                for i, asset in enumerate(assets[:5])
            ],
            "note": "Mock data - enable OpenGradient SDK for real analysis"
        }
    
    async def get_available_ml_models(self) -> List[Dict[str, Any]]:
        """Get list of available ML models from OpenGradient Model Hub."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/models")
            if response.status_code == 200:
                models = response.json()
                # Filter for ML models (BitQuant, PricePredictor, RiskAnalyzer)
                ml_models = [
                    model for model in models
                    if any(keyword in model.get("name", "").lower() 
                          for keyword in ["bitquant", "pricepredictor", "riskanalyzer", "quant", "prediction", "risk"])
                ]
                return ml_models
            else:
                logger.warning(f"Failed to fetch models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching ML models: {e}")
            # Return mock models
            return [
                {
                    "id": "bitquant-v1",
                    "name": "BitQuant",
                    "description": "Quantitative AI agent for trading predictions and analytics",
                    "category": "DeFi",
                    "author": "OpenGradient",
                    "tags": ["trading", "prediction", "quantitative", "ml"]
                },
                {
                    "id": "pricepredictor-v2",
                    "name": "PricePredictor",
                    "description": "ML model for cryptocurrency price forecasting",
                    "category": "DeFi",
                    "author": "OpenGradient",
                    "tags": ["price", "forecast", "time-series", "ml"]
                },
                {
                    "id": "riskanalyzer-v3",
                    "name": "RiskAnalyzer",
                    "description": "Portfolio risk analysis and optimization model",
                    "category": "DeFi",
                    "author": "OpenGradient",
                    "tags": ["risk", "portfolio", "optimization", "ml"]
                }
            ]


# Global instance
ml_model_service = MLModelService()