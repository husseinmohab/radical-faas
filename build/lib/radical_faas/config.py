"""
Manages centralized configuration for the RADICAL-FaaS application.

This module provides a single source of truth for application settings,
making it easy to manage configuration for different environments.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Defines the application settings using Pydantic."""
    # Store settings
    db_file: str = "radical_faas.db"

    # Builder settings
    # The default registry where function images will be pushed.
    # Replace this with your own Docker Hub username or private registry.
    container_registry: str = "docker.io/your-username"

    # Kubernetes settings
    job_namespace: str = "default"
    job_ttl_seconds_after_finished: int = 600 # 10 minutes

# Create a single, importable instance of the settings
settings = Settings()