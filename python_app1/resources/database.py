import logging
import typing

from sqlalchemy.ext import asyncio as sa

from models.tables import Base
from settings import Settings


logger = logging.getLogger(__name__)


async def create_sa_engine(settings: Settings) -> typing.AsyncIterator[sa.AsyncEngine]:
    logger.info("Initializing SQLAlchemy engine")
    engine = sa.create_async_engine(
        url=settings.db_dsn,
        echo=settings.debug,
        echo_pool=settings.debug,
        pool_size=settings.database_pool_size,
        pool_pre_ping=settings.database_pool_pre_ping,
        max_overflow=settings.database_max_overflow,
    )
    logger.info("SQLAlchemy engine has been initialized")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        await engine.dispose()
        logger.info("SQLAlchemy engine has been cleaned up")


async def create_session(engine: sa.AsyncEngine) -> typing.AsyncIterator[sa.AsyncSession]:
    async with sa.AsyncSession(engine, expire_on_commit=False, autoflush=False) as session:
        yield session