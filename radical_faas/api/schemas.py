"""
this module contains the schemas that define the expected structure for
request and response bodies, ensuring that all data exchanged with the API
is well-formed
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class FunctionCreate(BaseModel):
    """Schema for creating a new function."""
    name: str = Field(
        ...,
        description="The unique name of the function.",
        example="my-greeting-function"
    )
    runtime: str = Field(
        ...,
        description="The execution runtime for the function.",
        example="python:3.9-slim"
    )
    handler: str = Field(
        ...,
        description="The entry point for the function (e.g., 'main.handle').",
        example="main.handle"
    )
    code: str = Field(
        ...,
        description="A string containing the source code of the function."
    )
    dependencies: Optional[List[str]] = Field(
        default_factory=list,
        description="A list of pip-installable dependencies.",
        example=["requests", "numpy"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class InvokeRequest(BaseModel):
    """Schema for an invocation request payload."""
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="A JSON-serializable object to pass to the function as input."
    )


class FunctionResponse(BaseModel):
    """A standardized response schema for function-related operations."""
    status: str = Field(description="The status of the operation.", example="success")
    message: str = Field(description="A descriptive message.", example="Function deployed successfully.")
    details: Optional[Dict[str, Any]] = None