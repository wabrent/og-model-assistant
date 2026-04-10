#!/usr/bin/env python3
"""
Test OpenGradient API endpoints.
"""
import asyncio
import httpx
from core.config import settings

BASE_URL = "https://hub-api.opengradient.ai"
TIMEOUT = 10

async def test_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Test a specific API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if settings.private_key:
        headers["Authorization"] = f"Bearer {settings.private_key}"
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data or {})
            else:
                return {"error": f"Unsupported method {method}"}
            
            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:500] if response.text else None
            }
        except Exception as e:
            return {"endpoint": endpoint, "error": str(e)}

async def main():
    print(f"Testing OpenGradient API endpoints with key: {settings.private_key[:10]}...")
    
    endpoints = [
        "/",
        "/models",
        "/v1/models",
        "/api/models",
        "/api/v1/models",
        "/health",
        "/api/health",
        "/v1/health",
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}...")
        result = await test_endpoint(endpoint)
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Status: {result['status_code']}")
            if result['status_code'] == 200:
                print(f"  Body: {result['body'][:100]}...")
            elif result['status_code'] == 404:
                print(f"  Not Found")
            elif result['status_code'] == 401:
                print(f"  Unauthorized")
            elif result['status_code'] == 403:
                print(f"  Forbidden")
            else:
                print(f"  Headers: {result['headers']}")

if __name__ == "__main__":
    asyncio.run(main())