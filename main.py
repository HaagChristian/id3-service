import logging
import uuid

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from src.api.routers import metadata

version: str = "0.0.1"
app_name: str = "ID3 Service"
instance_uuid: str = str(uuid.uuid4())
app_description: str = "This is a simple service to extract metadata from mp3 files. "
contact_name: str = "Christian Haag"

app = FastAPI(
    title=app_name,
    description=app_description,
    version=version,
    docs_url="/api",
    contact={"name": contact_name},
)

app.include_router(metadata.router)

# CORS is required to run api simultaneously with website on local machine
# Allow localhost:8000 and 127.0.0.1:8000 to access the api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    logging.info("run main")
    uvicorn.run(app, port=3000)


@app.get("/")
def rootreq():
    return {"home"}


@app.get("/health")
def health(request: Request):
    correlation_id = request.headers.get("X-Correlation-ID", default="not set")


if __name__ == "__main__":
    main()
