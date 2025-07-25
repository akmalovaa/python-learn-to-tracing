import logging

from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.ext import asyncio as sa

from otel_py_example.settings import Settings, settings

logger = logging.getLogger(__name__)


def create_sa_engine(settings: Settings) -> sa.AsyncEngine:
    logger.info("Initializing SQLAlchemy async engine")
    return sa.create_async_engine(
        url=settings.db_dsn,
        echo=settings.debug,
        echo_pool=settings.debug,
        pool_size=settings.database_pool_size,
        pool_pre_ping=settings.database_pool_pre_ping,
        max_overflow=settings.database_max_overflow,
    )


def create_sync_sa_engine(settings: Settings):
    logger.info("Initializing SQLAlchemy sync engine")
    # Convert async URL to sync URL for instrumentation
    sync_dsn = settings.db_dsn.set(drivername="postgresql+psycopg2")
    return create_sync_engine(
        url=sync_dsn,
        echo=settings.debug,
        echo_pool=settings.debug,
        pool_size=settings.database_pool_size,
        pool_pre_ping=settings.database_pool_pre_ping,
        max_overflow=settings.database_max_overflow,
    )


database_engine = create_sa_engine(settings)
sync_database_engine = create_sync_sa_engine(settings)


async def create_session(engine: sa.AsyncEngine) -> sa.AsyncSession:
    return sa.AsyncSession(engine, expire_on_commit=False, autoflush=False)
