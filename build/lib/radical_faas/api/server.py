"""
The main FastAPI application setup.

This module creates the FastAPI app instance and includes the routers
for different parts of the API.
"""

from fastapi import FastAPI
from .endpoints import functions

# Create the main FastAPI application instance
app = FastAPI(
    title="RADICAL-FaaS",
    description="A standalone FaaS platform for running serverless functions on Kubernetes.",
    version="0.1.0"
)

# Include the router from the 'functions' endpoint module.
# All routes defined in that router will be added to the app.
app.include_router(functions.router, prefix="/api/v1", tags=["Functions"])


@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "RADICAL-FaaS API is running."}