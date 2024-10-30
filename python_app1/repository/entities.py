
import sqlalchemy as sa

from python_app1.models import tables

import logging
from sqlalchemy.ext import asyncio as sa_async
logger = logging.getLogger(__name__)

class EntitiesRepository:
    def __init__(self, engine: sa_async.AsyncEngine):
        self.model = tables.Entity
        self.engine = engine

    async def get_entity_by_id(self, entity_id: str) -> tables.Entity | None:
        async with self.engine.connect() as conn:
            query = sa.select(tables.Entity).where(tables.Entity.id == entity_id)
            result_cursor = await conn.execute(query)
            return result_cursor.scalars().first()
    
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
