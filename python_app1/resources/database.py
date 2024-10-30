import logging

from sqlalchemy.ext import asyncio as sa

from python_app1.settings import Settings, settings

logger = logging.getLogger(__name__)


def create_sa_engine(settings: Settings) -> sa.AsyncEngine:
    logger.info("Initializing SQLAlchemy engine")
    return sa.create_async_engine(
        url=settings.db_dsn,
        echo=settings.debug,
        echo_pool=settings.debug,
        pool_size=settings.database_pool_size,
        pool_pre_ping=settings.database_pool_pre_ping,
        max_overflow=settings.database_max_overflow,
    )


database_engine = create_sa_engine(settings) 


async def create_session(engine: sa.AsyncEngine) -> sa.AsyncSession:
    return sa.AsyncSession(engine, expire_on_commit=False, autoflush=False)
