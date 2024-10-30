import dataclasses

import sqlalchemy as sa

from models import tables

import dataclasses
import typing

from sqlalchemy.ext import asyncio as sa_async


T = typing.TypeVar("T", bound=tables.Base)


@dataclasses.dataclass(kw_only=True)
class BaseRepository(typing.Generic[T]):
    model: type[T] = dataclasses.field(init=False)
    session: sa_async.AsyncSession


@dataclasses.dataclass(kw_only=True)
class EntitiesRepository(BaseRepository[tables.Entity]):
    model = tables.Entity

    async def get_entity_by_id(self, entity_id: str) -> tables.Entity | None:
        query = sa.select(tables.Entity).where(tables.Entity.id == entity_id)
        result_cursor = await self.session.execute(query)
        return result_cursor.scalars().first()
