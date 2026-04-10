#!/usr/bin/env python3
"""
Test real OpenGradient ML API integration.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from services.ml_model_service import MLModelService


async def test_ml_service():
    """Test ML model service with real API key."""
    print(f"Testing ML Model Service with API key: {settings.private_key[:10]}...")
    
    service = MLModelService()
    
    # Test 1: Get available ML models
    print("\n1. Testing get_available_ml_models()...")
    try:
        models = await service.get_available_ml_models()
        print(f"   Found {len(models)} models")
        for model in models[:3]:
            print(f"   - {model.get('name')} ({model.get('id')})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Call BitQuant (mock for now)
    print("\n2. Testing call_bitquant()...")
    try:
        prediction = await service.call_bitquant("ETH/USDT", "24h")
        print(f"   Prediction for ETH/USDT: {prediction.get('predicted_price')}")
        print(f"   Model: {prediction.get('model_name')}")
        print(f"   Note: {prediction.get('note', 'No note')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Call PricePredictor
    print("\n3. Testing call_price_predictor()...")
    try:
        prediction = await service.call_price_predictor("SUI/USDT", "24h")
        print(f"   Prediction for SUI/USDT: {prediction.get('predicted_price')}")
        print(f"   Model: {prediction.get('model_name')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Call RiskAnalyzer
    print("\n4. Testing call_risk_analyzer()...")
    try:
        portfolio = {
            "id": "test_portfolio",
            "assets": [
                {"symbol": "ETH", "amount": 10, "value_usd": 35000},
                {"symbol": "SUI", "amount": 1000, "value_usd": 1200},
                {"symbol": "BTC", "amount": 0.5, "value_usd": 25000},
            ]
        }
        analysis = await service.call_risk_analyzer(portfolio)
        print(f"   Risk score: {analysis.get('risk_score')}")
        print(f"   Risk level: {analysis.get('risk_level')}")
        print(f"   Recommendations: {analysis.get('recommendations')[:1]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    await service.close()
    print("\nTest completed.")


if __name__ == "__main__":
    asyncio.run(test_ml_service())