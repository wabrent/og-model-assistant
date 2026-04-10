#!/usr/bin/env python3
"""
Test real OpenGradient workflow models.
"""
import asyncio
import opengradient as og
from core.config import settings

async def test_workflow():
    """Test reading from a real workflow model."""
    print(f"Testing with private key: {settings.private_key[:10]}...")
    
    # Create Alpha instance
    alpha = og.Alpha(private_key=settings.private_key)
    print(f"Alpha created: {alpha}")
    
    # Test 1: Read from ETH 1-hour price forecast workflow
    print("\n1. Reading ETH 1-hour price forecast...")
    try:
        # Use contract address from workflow_models.constants
        from opengradient.workflow_models.constants import ETH_1_HOUR_PRICE_FORECAST_ADDRESS
        contract_address = ETH_1_HOUR_PRICE_FORECAST_ADDRESS
        print(f"   Contract address: {contract_address}")
        
        # Read workflow result
        result = alpha.read_workflow_result(contract_address)
        print(f"   Result type: {type(result)}")
        print(f"   Result: {result}")
        
        # Try to extract numbers
        if hasattr(result, 'numbers'):
            print(f"   Numbers: {result.numbers}")
        
    except ImportError:
        print("   Could not import constants")
    except Exception as e:
        print(f"   Error reading workflow: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try to run workflow (might cost gas)
    print("\n2. Trying to run workflow (read-only, no gas)...")
    try:
        # Use a different address for volatility
        from opengradient.workflow_models.constants import ETH_USDT_1_HOUR_VOLATILITY_ADDRESS
        contract_address = ETH_USDT_1_HOUR_VOLATILITY_ADDRESS
        
        # read_workflow_history
        history = alpha.read_workflow_history(contract_address)
        print(f"   Workflow history: {history[:200]}...")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Try to infer with a model CID (if we can find one)
    print("\n3. Trying to find any model CID...")
    try:
        # Look for model CID in environment or config
        # For now, try to use the contract address as model_cid? Probably not.
        # Let's check if there's a default model CID in SDK
        # We'll skip for now
        print("   Need model CID for inference.")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Use workflow_models package functions
    print("\n4. Using workflow_models package...")
    try:
        from opengradient.workflow_models import read_eth_1_hour_price_forecast
        output = read_eth_1_hour_price_forecast(alpha)
        print(f"   Output: {output}")
        print(f"   Result: {output.result}")
        print(f"   Block explorer link: {output.block_explorer_link}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_workflow())