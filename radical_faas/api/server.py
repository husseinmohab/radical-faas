"""
main fastapi application setup

this module creates the fastapi app instance and includes the routers
for different parts of the api
"""

from fastapi import FastAPI
from .endpoints import functions

# create fastapi app instance
app = FastAPI(title="RADICAL-FaaS")

# include router from the 'functions' endpoint module, all routes defined in that router will be added to the app
app.include_router(functions.router, prefix="/api/v1", tags=["Functions"])


@app.get("/", tags=["Health Check"])
async def read_root():
    """health check endpoint to confirm the API is running"""
    return {"status": "RADICAL-FaaS API is running"}