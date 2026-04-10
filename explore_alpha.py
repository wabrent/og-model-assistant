#!/usr/bin/env python3
"""
Explore Alpha class in OpenGradient SDK.
"""
import opengradient as og
import inspect
from core.config import settings

print("Exploring Alpha class...")
print("=" * 50)

# Get Alpha class
Alpha = og.Alpha
print(f"Alpha class: {Alpha}")

# Inspect __init__ signature
try:
    sig = inspect.signature(Alpha.__init__)
    print(f"\nAlpha.__init__ signature:")
    print(f"  {sig}")
except Exception as e:
    print(f"  Error: {e}")

# Try to instantiate Alpha with private key
print("\nInstantiating Alpha...")
try:
    alpha = Alpha(private_key=settings.private_key)
    print(f"  Alpha instance: {alpha}")
    
    # Check methods
    print("\n  Alpha methods:")
    for attr in dir(alpha):
        if not attr.startswith('_'):
            obj = getattr(alpha, attr)
            print(f"    {attr}: {type(obj).__name__}")
    
    # Inspect 'infer' method
    if hasattr(alpha, 'infer'):
        infer_method = alpha.infer
        print(f"\n  infer method: {infer_method}")
        try:
            sig = inspect.signature(infer_method)
            print(f"    Signature: {sig}")
        except:
            pass
        
        # Try to call infer with dummy data
        print("\n  Testing infer with dummy data...")
        try:
            # Need model_cid and inputs
            # Try to find example model CID from SDK or docs
            # Let's try a placeholder
            result = alpha.infer(
                model_cid="QmTest",  # Placeholder CID
                inputs={"symbol": "ETH/USDT", "horizon": "24h"}
            )
            print(f"    Result: {result}")
        except Exception as e:
            print(f"    Error calling infer: {e}")
            import traceback
            traceback.print_exc()
    
    # Inspect 'run_workflow'
    if hasattr(alpha, 'run_workflow'):
        print(f"\n  run_workflow method exists")
        try:
            sig = inspect.signature(alpha.run_workflow)
            print(f"    Signature: {sig}")
        except:
            pass
    
except Exception as e:
    print(f"  Error instantiating Alpha: {e}")
    import traceback
    traceback.print_exc()

# Check if there are predefined model CIDs in SDK
print("\n" + "=" * 50)
print("Looking for predefined models in SDK...")

# Search for constants in opengradient module
import opengradient
for attr in dir(opengradient):
    if 'BIT' in attr or 'QUANT' in attr or 'PRICE' in attr or 'RISK' in attr or 'MODEL' in attr:
        obj = getattr(opengradient, attr)
        print(f"  {attr}: {obj}")

# Check types module
if hasattr(opengradient, 'types'):
    types = opengradient.types
    print("\n  Types module attributes:")
    for attr in dir(types):
        if 'MODEL' in attr or 'CID' in attr:
            obj = getattr(types, attr)
            print(f"    {attr}: {obj}")

# Check client module
if hasattr(opengradient, 'client'):
    client = opengradient.client
    print("\n  Client module attributes:")
    for attr in dir(client):
        if 'MODEL' in attr:
            obj = getattr(client, attr)
            print(f"    {attr}: {obj}")

# Check if there's a model registry
print("\n" + "=" * 50)
print("Checking for model registry...")

# Try to import ModelHub and see if we can list models with email/password
# But we don't have credentials. Maybe there's a public endpoint.
# Let's try to fetch from a public API
import httpx
import asyncio

async def fetch_public_models():
    """Try to fetch public model list."""
    urls = [
        "https://hub-api.opengradient.ai/public/models",
        "https://api.opengradient.ai/models",
        "https://api.opengradient.ai/v1/models",
    ]
    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                resp = await client.get(url, timeout=10)
                if resp.status_code == 200:
                    print(f"  Found models at {url}")
                    print(f"    Response: {resp.json()[:200]}")
                    return
                else:
                    print(f"  {url}: {resp.status_code}")
            except Exception as e:
                print(f"  {url}: error {e}")

print("\nTrying public model endpoints...")
asyncio.run(fetch_public_models())