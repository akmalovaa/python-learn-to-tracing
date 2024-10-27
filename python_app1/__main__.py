import sys
import uvicorn
from fastapi import FastAPI

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:DD.MM.YY HH:mm:ss} {level} {message}",
)

app = FastAPI()
service_name = "fastapi-app"
logger.info(f"{service_name} started, listening on port 8000")

@app.get("/")
def root_endpoint():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
