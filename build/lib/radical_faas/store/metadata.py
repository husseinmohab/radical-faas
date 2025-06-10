"""
Manages the persistence of function metadata using a SQLite database.

This module provides an interface for the controller to create, read, and
update records for deployed functions, ensuring that the platform's state
is saved between restarts.
"""

import sqlite3
from typing import Dict, Optional, List, Any

from ..config import settings


_db_connection: Optional[sqlite3.Connection] = None


def _get_db_connection() -> sqlite3.Connection:
    """Creates or returns a cached database connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect(settings.db_file)
        _db_connection.row_factory = sqlite3.Row
    return _db_connection


def init_db():
    """Initializes the database and creates the 'functions' table."""
    print("Store: Initializing database...")
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            name TEXT PRIMARY KEY NOT NULL,
            image_uri TEXT NOT NULL,
            handler TEXT NOT NULL,
            runtime TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print(f"Store: Database initialized at '{settings.db_file}'.")


async def save_function_details(name: str, image_uri: str, handler: str, runtime: str) -> None:
    """
    Saves or updates a function's details in the database.

    Args:
        name: The unique name of the function.
        image_uri: The URI of the container image for the function.
        handler: The function's entry point (e.g., 'main.handle').
        runtime: The function's language runtime (e.g., 'python3.9').
    """
    print(f"Store: Saving details for function '{name}'.")
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO functions (name, image_uri, handler, runtime) VALUES (?, ?, ?, ?)",
        (name, image_uri, handler, runtime)
    )
    conn.commit()


async def get_function_details(function_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the details for a single function from the database.

    Args:
        function_name: The name of the function to retrieve.

    Returns:
        A dictionary containing the function's details, or None if not found.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM functions WHERE name = ?", (function_name,))
    row = cursor.fetchone()
    return dict(row) if row else None


async def list_all_functions() -> List[Dict[str, Any]]:
    """
    Retrieves a list of all deployed functions.

    Returns:
        A list of dictionaries, where each dictionary represents a function.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM functions")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]