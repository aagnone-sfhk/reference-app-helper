"""
This module is the main entry point for the AppLink Python Starter aplication.

It initializes a main FastAPI application for public endpoints and mounts a
sub-application for all endpoints that require Salesforce context.
"""
import heroku_applink as sdk
from fastapi import FastAPI
from typing import Dict
import yaml

from .routers import accounts, unitofwork, datacloud

# --- Protected Salesforce App ---
# All routers and middleware that require Salesforce context are attached here.
sf_app = FastAPI()
sf_app.add_middleware(sdk.IntegrationAsgiMiddleware, config=sdk.Config())

# THIS IS THE FIX:
# We need to tell the sub-app how to route to these routers.
sf_app.include_router(accounts.router, prefix="/accounts")
sf_app.include_router(unitofwork.router, prefix="/unitofwork")

# --- Main Public App ---
app = FastAPI(
    title="AppLink Python Starter",
    description="A starter project for building Salesforce-integrated applications with Heroku AppLink.",
    version="1.0.0"
)

# Mount the protected Salesforce app at the /api prefix
app.mount("/api", sf_app)

# The Data Cloud router is a webhook, so it's attached to the main app
# without the Salesforce context middleware.
app.include_router(datacloud.router)

# Load the OpenAPI spec and attach it to the main app
with open("api-spec.yaml", "r") as f:
    openapi_schema = yaml.safe_load(f)
app.openapi_schema = openapi_schema

@app.get("/", summary="Welcome endpoint")
def read_root() -> Dict[str, str]:
    """
    A welcoming root endpoint that is publicly accessible.
    
    :return: A welcome message.
    :rtype: Dict[str, str]
    """
    return {
        "message": "Welcome to the AppLink Python Starter!",
        "docs_url": "/docs",
        "salesforce_api_prefix": "/api"
    }

@app.get("/health", summary="Health check endpoint")
def get_health() -> Dict[str, str]:
    """
    A simple health check endpoint.

    :return: A dictionary with a status of "ok".
    :rtype: Dict[str, str]
    """
    return {"status": "ok"}
