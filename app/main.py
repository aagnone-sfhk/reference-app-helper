"""
This module is the main entry point for the AppLink Python Starter aplication.

It initializes the FastAPI application, loads the OpenAPI specification,
and includes the API routers.
"""
import heroku_applink as sdk
from fastapi import FastAPI, Response
from typing import Dict, Any

from .routers import accounts, unitofwork, datacloud

import yaml

config = sdk.Config()

app = FastAPI(
    title="AppLink Python Starter",
    description="A starter project for building Salesforce-integrated applications with Heroku AppLink.",
    version="1.0.0"
)

with open("api-spec.yaml", "r") as f:
    openapi_schema = yaml.safe_load(f)
app.openapi_schema = openapi_schema

app.add_middleware(sdk.IntegrationAsgiMiddleware, config=config)

app.include_router(accounts.router)
app.include_router(unitofwork.router)
app.include_router(datacloud.router)

@app.get("/health", summary="Health check endpoint")
def get_health() -> Dict[str, str]:
    """
    A simple health check endpoint.

    :return: A dictionary with a status of "ok".
    :rtype: Dict[str, str]
    """
    return {"status": "ok"}
