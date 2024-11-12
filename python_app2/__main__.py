from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from python_app2.pokeapi_client import (
    PokeapiClient,
    PokemonResponse
)
from loguru import logger
import uvicorn
import pydantic
from python_app2.utils import setting_otlp
import os

service_name = "fastapi-app-2"
OTLP_ENDPOINT: str = os.environ.get("OTLP_ENDPOINT", "http://otel-collector:4317")

app = FastAPI(debug=True)

# Setting OpenTelemetry exporter
tracer = setting_otlp(app, "app2", OTLP_ENDPOINT)


class SecondAppPayload(pydantic.BaseModel):
    entity_id: str
    value: str


@app.get("/pokemon/{pokemon_name}")
async def get_pokemon_info(pokemon_name: str):
    return await PokeapiClient.retrieve_pokemon_info(pokemon_name)


@app.get("/entity/")
async def retrieve_entity_by_id(entity_id: str):
    return f"Entity with id: {entity_id}"


@app.post("/entity/")
async def update_entity_by_id(income: SecondAppPayload):
    return f"Entity with id: {income.entity_id} updated with value {income.value}"


@app.post("/entity/bad-blood/")
async def wanna_error():
    raise HTTPException(status_code=401, detail="Just a generic error")


if __name__ == "__main__":
    logger.info(f"{service_name} start, listening on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
