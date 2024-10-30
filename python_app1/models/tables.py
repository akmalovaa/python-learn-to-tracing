import typing

import sqlalchemy as sa
from sqlalchemy import orm


METADATA: sa.MetaData = sa.MetaData()


class Base(orm.DeclarativeBase):
    metadata = METADATA


class BaseModel(Base):
    __abstract__ = True

    id: orm.Mapped[typing.Annotated[int, orm.mapped_column(primary_key=True)]]

    def __str__(self) -> str:
        return f"<{type(self).__name__}({self.id=})>"


class Entity(BaseModel):
    __tablename__ = "entities"

    name: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    description: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=True)
