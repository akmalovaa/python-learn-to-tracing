import httpx
from python_app1.settings import settings


async def fetch_data_service_2(entity_id: int):
    async with httpx.AsyncClient() as client:
        result = await client.get(f'http://{settings.second_app_host}:8001/entity/', params={"entity_id": entity_id})
        print(f"Result is {result}, {result.text}")
    return result.json()


async def update_data_service_2(entity_id: str, value: str):
    async with httpx.AsyncClient() as client:
        result = await client.post(f'http://{settings.second_app_host}:8001/entity/', json={"entity_id": entity_id, "value": value})
        print(f"Result is {result}, {result.text}")
    return result.json()


async def call_error():
    async with httpx.AsyncClient() as client:
        result = await client.post(f'http://{settings.second_app_host}:8001/entity/bad-blood/')
        print(f"Result is {result}, {result.text}")
    return result.json()