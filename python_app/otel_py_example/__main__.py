# import asyncio
import asyncio
import os
import random
import sys
import time
from typing import Any, Dict, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from opentelemetry.propagate import inject

from otel_py_example.utils import setting_otlp
from otel_py_example.models import tables
from otel_py_example.clients import fetch_data_service_2, update_data_service_2, call_error
from otel_py_example.middleware import TraceIDMiddleware, get_trace_id_from_request, get_current_trace_id

from otel_py_example.repository.entities import EntitiesRepository, EntitiesAsyncpgRepo
from otel_py_example.resources.database import database_engine, sync_database_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from otel_py_example.repository.redis_repo import RedisRepo
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

# Add CORS middleware
# Setting OpenTelemetry exporter
tracer = setting_otlp(app, APP_NAME, OTLP_ENDPOINT)

# Add TraceID middleware for handling frontend trace_id (должен быть перед CORS)
app.add_middleware(TraceIDMiddleware)

# Add CORS middleware (должен быть последним)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


SQLAlchemyInstrumentor().instrument(
    engine=sync_database_engine,
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
def root_endpoint(request: Request):
    # Получаем trace_id из фронтенда
    frontend_trace_id = get_trace_id_from_request(request)
    current_trace_id = get_current_trace_id()

    logger.info(f"Root endpoint called - Frontend trace_id: {frontend_trace_id}, Backend trace_id: {current_trace_id}")

    return {
        "message": "Hello World",
        "trace_info": {"frontend_trace_id": frontend_trace_id, "backend_trace_id": current_trace_id},
    }


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


class SecondAppPayload(pydantic.BaseModel):
    entity_id: str
    value: str


@app.get("/entities/")
async def get_all_entities(request: Request):
    # Получаем trace_id из фронтенда
    frontend_trace_id = get_trace_id_from_request(request)
    current_trace_id = get_current_trace_id()

    logger.info(f"Getting all entities - Frontend trace_id: {frontend_trace_id}, Backend trace_id: {current_trace_id}")

    handler = EntitiesHandler()
    await handler.init_all()
    entities = await handler.get_all_entities()
    return {
        "entities": entities,
        "trace_info": {"frontend_trace_id": frontend_trace_id, "backend_trace_id": current_trace_id},
    }


@app.get("/entities/{entity_id}/")
async def get_entity_by_id(entity_id: str):
    handler = EntitiesHandler()
    await handler.init_all()
    entity = await handler.get_entity_by_id(entity_id)
    return {"entity": entity}


@app.post("/entities/")
async def create_entity(income: EntityCreateModel, request: Request):
    # Получаем trace_id из фронтенда
    frontend_trace_id = get_trace_id_from_request(request)
    current_trace_id = get_current_trace_id()

    logger.info(
        f"Creating entity '{income.name}' - Frontend trace_id: {frontend_trace_id}, Backend trace_id: {current_trace_id}"
    )

    handler = EntitiesHandler()
    await handler.init_all()

    res = await handler.create_entity(income.name, income.description)
    return {"entity": res, "trace_info": {"frontend_trace_id": frontend_trace_id, "backend_trace_id": current_trace_id}}


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


@app.get("/second-app/")
async def fetch_second_app(entity_id: int):
    res = await fetch_data_service_2(entity_id=entity_id)
    return {"res": res}


@app.post("/second-app/")
async def update_second_app(income: SecondAppPayload):
    res = await update_data_service_2(income.entity_id, income.value)
    return {"res": res}


@app.post("/second-app/error/")
async def call_error_second_app():
    res = await call_error()
    return {"res": res}


if __name__ == "__main__":
    logger.info(f"{service_name} start, listening on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT)
