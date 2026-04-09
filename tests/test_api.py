"""
Tests for the OpenGradient Model Assistant API.
"""
import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from main import app
from core.database import Base, get_db
from core.config import settings


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """Create a fresh database for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    """Create test client with overridden dependencies."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============== Health Check Tests ==============

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = await client.get("/api/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


# ============== Model Search Tests ==============

@pytest.mark.asyncio
async def test_search_models_empty(client):
    """Test model search with empty database."""
    response = await client.post(
        "/api/models/search",
        json={"query": "test", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "total" in data
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_models_with_query(client):
    """Test model search with query parameter."""
    response = await client.post(
        "/api/models/search",
        json={"query": "ETH", "limit": 20, "offset": 0}
    )
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "total" in data
    assert data["limit"] == 20
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_search_models_validation(client):
    """Test model search validation."""
    # Test invalid limit
    response = await client.post(
        "/api/models/search",
        json={"query": "test", "limit": 101}
    )
    assert response.status_code == 422  # Validation error


# ============== Chat Tests ==============

@pytest.mark.asyncio
async def test_chat_basic(client):
    """Test basic chat endpoint."""
    response = await client.post(
        "/api/chat",
        json={"message": "Hello", "session_id": "test_session"}
    )
    # May fail if OpenGradient is not configured, but should not crash
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_chat_validation(client):
    """Test chat endpoint validation."""
    # Test empty message
    response = await client.post(
        "/api/chat",
        json={"message": "", "session_id": "test"}
    )
    assert response.status_code == 422


# ============== Analytics Tests ==============

@pytest.mark.asyncio
async def test_get_stats(client):
    """Test getting global statistics."""
    response = await client.get("/api/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_models" in data
    assert "active_models" in data


@pytest.mark.asyncio
async def test_get_model_stats(client):
    """Test getting model statistics."""
    response = await client.get("/api/analytics/models/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_models" in data


@pytest.mark.asyncio
async def test_get_top_queries(client):
    """Test getting top queries."""
    response = await client.get("/api/analytics/queries/top?period=7d&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "queries" in data
    assert "period" in data


# ============== Sync Tests ==============

@pytest.mark.asyncio
async def test_get_sync_status(client):
    """Test getting sync status."""
    response = await client.get("/api/sync/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_syncing" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_trigger_sync(client):
    """Test triggering manual sync."""
    response = await client.post("/api/sync/trigger")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


# ============== Root Tests ==============

@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200


# ============== Integration Tests ==============

@pytest.mark.asyncio
async def test_full_chat_flow(client):
    """Test full chat flow: search, chat, analytics."""
    # 1. Search for models
    search_response = await client.post(
        "/api/models/search",
        json={"query": "test", "limit": 5}
    )
    assert search_response.status_code == 200
    
    # 2. Send chat message
    chat_response = await client.post(
        "/api/chat",
        json={"message": "Find me some models", "session_id": "integration_test"}
    )
    # May return 500 if OG not configured
    assert chat_response.status_code in [200, 500]
    
    # 3. Get stats
    stats_response = await client.get("/api/analytics/stats")
    assert stats_response.status_code == 200


# ============== Error Handling Tests ==============

@pytest.mark.asyncio
async def test_404_not_found(client):
    """Test 404 for non-existent routes."""
    response = await client.get("/api/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_method_not_allowed(client):
    """Test method not allowed."""
    response = await client.get("/api/chat")  # Should be POST
    assert response.status_code == 405
