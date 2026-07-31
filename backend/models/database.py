import structlog
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from backend.config import settings

logger = structlog.get_logger()

# Create SQLAlchemy Async Engine
engine_args = {
    "echo": False,
    "future": True,
}
if not settings.async_db_url.startswith("sqlite"):
    engine_args["pool_size"] = 20
    engine_args["max_overflow"] = 10

engine = create_async_engine(
    settings.async_db_url,
    **engine_args
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables (useful for dev, migrations in prod)."""
    import backend.models.orm  # noqa: F401
    
    logger.info(f"Connecting to database at {settings.async_db_url.split('@')[-1] if '@' in settings.async_db_url else 'sqlite'}")
    if not settings.async_db_url.startswith("sqlite"):
        logger.info("PostgreSQL configured; skipping metadata create_all. Run Alembic migrations before startup.")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas initialized.")
