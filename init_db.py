"""
Database initialization script.
Run this to create tables on first setup.
"""
import asyncio
from core.database import init_db, engine
from models.db_models import Base


async def reset_db():
    """Drop all tables and recreate."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database reset successfully!")


async def create_tables():
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("⚠️  Resetting database (all data will be lost)...")
        asyncio.run(reset_db())
    else:
        print("Creating database tables...")
        asyncio.run(create_tables())
