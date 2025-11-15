"""SQLAlchemy database configuration with optimized connection pooling."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from pathlib import Path
from app.logging_config import get_logger

logger = get_logger(__name__)

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/mathai.db"

# Create async engine with optimized settings
# Note: SQLite doesn't benefit from traditional connection pooling like PostgreSQL
# Using NullPool for SQLite to avoid connection conflicts
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    poolclass=NullPool,  # Best for SQLite with async operations
    connect_args={
        "check_same_thread": False,  # Required for SQLite with multiple threads
        "timeout": 30,  # Connection timeout in seconds
    },
)

# For production with PostgreSQL, use these settings instead:
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=False,
#     future=True,
#     pool_size=20,              # Number of permanent connections
#     max_overflow=10,           # Maximum additional connections
#     pool_pre_ping=True,        # Verify connections before use
#     pool_recycle=3600,         # Recycle connections after 1 hour
#     pool_timeout=30,           # Timeout waiting for connection
#     echo_pool=True,            # Log connection pool events
# )

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    logger.info("Initializing database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully")
