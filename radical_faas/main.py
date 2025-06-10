"""
The main entry point for running the RADICAL-FaaS server.
"""

import uvicorn
from .store.metadata import init_db


def main():
    """Initializes dependencies and starts the web server."""
    # Initialize the database before starting the web server.
    init_db()

    # uvicorn is a high-performance ASGI server used to run FastAPI apps.
    # "radical_faas.api.server:app" tells uvicorn where to find the FastAPI app instance.
    # --reload makes the server restart automatically when you change the code.
    uvicorn.run(
        "radical_faas.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()