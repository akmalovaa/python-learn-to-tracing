import sqlalchemy as sa

from otel_py_example.models import tables
import asyncpg
from otel_py_example.settings import settings
import logging
from sqlalchemy.ext import asyncio as sa_async

logger = logging.getLogger(__name__)


class EntitiesRepository:
    def __init__(self, engine: sa_async.AsyncEngine):
        self.model = tables.Entity
        self.engine = engine

    async def get_entity_by_id(self, entity_id: str) -> tables.Entity | None:
        async with self.engine.connect() as conn:
            query = sa.select(tables.Entity).where(tables.Entity.id == int(entity_id))
            result_cursor = await conn.execute(query)
            return result_cursor.scalar()

    async def get_all_entities(self) -> list[tables.Entity]:
        async with self.engine.connect() as conn:
            query = sa.select(tables.Entity)
            result_cursor = await conn.execute(query)
            return result_cursor.mappings().all()

    async def create_entity(self, name: str, description: str) -> tables.Entity:
        entity = tables.Entity(name=name, description=description)
        async with self.engine.connect() as conn:
            conn.add(entity)
            await conn.commit()
            return entity


class EntitiesAsyncpgRepo:
    def __init__(self):
        self.conn = None

    async def init(self):
        self.conn = await asyncpg.connect(settings.database_dsn)

    async def get_entity_by_id(self, entity_id: str) -> tables.Entity | None:
        query = "SELECT * FROM entities WHERE id = $1"
        result = await self.conn.fetchrow(query, int(entity_id))
        if result:
            return tables.Entity(**result)
        return None

    async def get_all_entities(self) -> list[tables.Entity]:
        query = "SELECT * FROM entities"
        result = await self.conn.fetch(query)
        return [tables.Entity(**one_result) for one_result in result]

    async def create_entity(self, name: str, description: str) -> tables.Entity:
        query = "INSERT INTO entities (name, description) VALUES ($1, $2) RETURNING *"
        result = await self.conn.fetchrow(query, name, description)
        return tables.Entity(**result)
