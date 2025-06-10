"""
Defines the API endpoints for function management and invocation.

This module creates a router that handles all API requests related to
deploying, listing, and invoking functions.
"""

from fastapi import APIRouter, HTTPException, status
# --- CHANGE IS HERE ---
# Import the 'orchestrator' module directly from the 'controller' package
from ...controller import orchestrator
from .. import schemas

# Create a new router instance. This helps in organizing endpoints.
router = APIRouter()


@router.post(
    "/functions",
    response_model=schemas.FunctionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Deploy a New Function"
)
async def deploy_function(function_data: schemas.FunctionCreate):
    """Accepts a request to deploy a new function."""
    try:
        # --- CHANGE IS HERE ---
        # Call the function directly from the imported orchestrator module
        await orchestrator.deploy_new_function(function_data)
        return schemas.FunctionResponse(
            status="success",
            message=f"Deployment process for '{function_data.name}' has been initiated."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start deployment: {e}"
        )


@router.post(
    "/functions/{function_name}/invoke",
    response_model=schemas.FunctionResponse,
    summary="Invoke a Deployed Function"
)
async def invoke_function(function_name: str, invoke_data: schemas.InvokeRequest):
    """Accepts a request to invoke a deployed function."""
    try:
        # --- CHANGE IS HERE ---
        # Call the function directly from the imported orchestrator module
        result_details = await orchestrator.schedule_and_run_function(
            function_name, invoke_data.payload
        )
        return schemas.FunctionResponse(
            status="success",
            message=f"Function '{function_name}' invoked successfully.\n",
            details=result_details
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invoke function: {e}\n"
        )