# import asyncio
import asyncio
import os
import random
import sys
import time
from typing import Any, Dict, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Response
from loguru import logger
from opentelemetry.propagate import inject

from python_app1.utils import setting_otlp
from python_app1.models import tables
from python_app1.repository.entities import EntitiesRepository, EntitiesAsyncpgRepo
from python_app1.resources.database import database_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from python_app1.repository.redis_repo import RedisRepo
from opentelemetry.instrumentation.redis import RedisInstrumentor

import pydantic
APP_NAME: str = os.environ.get("APP_NAME", "app")
EXPOSE_PORT: int = int(os.environ.get("EXPOSE_PORT", 8000))
OTLP_ENDPOINT: str = os.environ.get("OTLP_ENDPOINT", "http://otel-collector:4317")
# http://localhost:4317 for local running

TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:DD.MM.YY HH:mm:ss} {level} {message}",
)


app = FastAPI()
service_name = "fastapi-app"

# Setting OpenTelemetry exporter
tracer = setting_otlp(app, APP_NAME, OTLP_ENDPOINT)



SQLAlchemyInstrumentor().instrument(
    engine=database_engine.sync_engine,
    tracer_provider=tracer,
    enable_commenter=True,
    commenter_options={},
)
# Instrument redis
RedisInstrumentor().instrument(tracer_provider=tracer)

class EntitiesHandler:

    def __init__(self):
        self.repository = None

    async def init_all(self):
        self.repository = EntitiesRepository(database_engine)
    
    async def get_entity_by_id(self, entity_id: str) -> dict | None:
        result = await self.repository.get_entity_by_id(entity_id)
        print(f"\n\nAFDDADAFDF {result=}\n\n")
        if result:
            return {"name": result.name, "description": result.description, "id": result.id}
        return None

    async def get_all_entities(self) -> list[dict]:
        data = await self.repository.get_all_entities()
        result = []
        for one_data in data:
            result.append({"name": one_data.name, "description": one_data.description, "id": one_data.id})
        return result
    
    async def create_entity(self, name: str, description: str) -> bool:
        async_session = async_sessionmaker(database_engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                session.add(tables.Entity(name=name, description=description))
                await session.commit()
        return True
    

class EntitiesHandlerAsyncpg:
    
        def __init__(self):
            self.repository = None
    
        async def init_all(self):
            self.repository = EntitiesAsyncpgRepo()
            await self.repository.init()
        
        async def get_entity_by_id(self, entity_id: str) -> dict | None:
            result = await self.repository.get_entity_by_id(entity_id)
            if result:
                return {"name": result.name, "description": result.description, "id": result.id}
            return None
    
        async def get_all_entities(self) -> list[dict]:
            data = await self.repository.get_all_entities()
            result = []
            for one_data in data:
                result.append({"name": one_data.name, "description": one_data.description, "id": one_data.id})
            return result
        
        async def create_entity(self, name: str, description: str) -> bool:
            result = await self.repository.create_entity(name, description)
            print("created entity = ", result)
            return True
    

@app.get("/")
def root_endpoint():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    logger.error("items")
    return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
    time.sleep(1)
    logger.error("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
    for i in range(1000):
        _ = i * i * i
    logger.error("cpu task")
    return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
    status_code = random.choice([200, 300, 400, 500])
    response.status_code = status_code
    logger.info(f"Random status code: {status_code}")
    {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
    sleep_duration = random.uniform(0, 5)
    await asyncio.sleep(sleep_duration)
    logger.info(f"random sleep time: {sleep_duration}")
    return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
    logger.error("got error!!!!")
    raise ValueError("value error")


@app.get("/chain")
async def chain(response: Response):
    headers: Dict[str, Any] = {}
    inject(headers)  # inject trace info to header
    logger.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
            headers=headers,
        )
    # async with httpx.AsyncClient() as client:
    #     await client.get(
    #         f"http://{TARGET_ONE_HOST}:8000/io_task",
    #         headers=headers,
    #     )
    # async with httpx.AsyncClient() as client:
    #     await client.get(
    #         f"http://{TARGET_TWO_HOST}:8000/cpu_task",
    #         headers=headers,
    #     )
    logger.info("Chain Finished")
    return {"path": "/chain"}


class EntityCreateModel(pydantic.BaseModel):
    name: str
    description: str


@app.get("/entities/")
async def get_all_entities():
    handler = EntitiesHandler()
    await handler.init_all()
    entities = await handler.get_all_entities()
    return {"entities": entities}


@app.get("/entities/{entity_id}/")
async def get_entity_by_id(entity_id: str):
    handler = EntitiesHandler()
    await handler.init_all()
    entity = await handler.get_entity_by_id(entity_id)
    return {"entity": entity}


@app.post("/entities/")
async def create_entity(
    income: EntityCreateModel
):
    handler = EntitiesHandler()
    await handler.init_all()

    res = await handler.create_entity(income.name, income.description)
    return {"entity": res}


@app.get("/entities-asyncpg/")
async def get_all_entities():
    handler = EntitiesHandlerAsyncpg()
    await handler.init_all()
    entities = await handler.get_all_entities()
    return {"entities": entities}


@app.get("/entities-asyncpg/{entity_id}/")
async def get_entity_by_id(entity_id: str):
    handler = EntitiesHandlerAsyncpg()
    await handler.init_all()
    entity = await handler.get_entity_by_id(entity_id)
    return {"entity": entity}


@app.post("/entities-asyncpg/")
async def create_entity(name: str, description: str):
    handler = EntitiesHandlerAsyncpg()
    await handler.init_all()

    res = await handler.create_entity(name, description)
    return {"entity": res}


@app.get("/redis-get/")
async def get_redis_value():
    handler = RedisRepo()

    entity = await handler.get_value()
    return {"entity": entity}


@app.post("/redis-set/")
async def set_redis_value(value: str):
    handler = RedisRepo()

    res = await handler.set_val(value)
    return {"res": res}


@app.post("/redis-delete/")
async def delete_redis_value():
    handler = RedisRepo()

    res = await handler.delete_value()
    return {"res": res}


if __name__ == "__main__":
    logger.info(f"{service_name} start, listening on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT)
