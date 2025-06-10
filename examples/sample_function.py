"""A sample function to be deployed on RADICAL-FaaS."""

def handle(payload: dict) -> dict:
    """
    A simple function that performs an operation on a list of numbers.

    Args:
        payload: A dictionary expected to contain 'operation' and 'numbers'.
                 - 'operation' can be 'sum' or 'multiply'.
                 - 'numbers' should be a list of integers or floats.

    Returns:
        A dictionary containing the result or an error message.
    """
    operation = payload.get("operation")
    numbers = payload.get("numbers", [])

    if not isinstance(numbers, list):
        return {"error": "Input 'numbers' must be a list."}

    if operation == "sum":
        result = sum(numbers)
        return {"operation": "sum", "result": result}
    elif operation == "multiply":
        result = 1
        for num in numbers:
            result *= num
        return {"operation": "multiply", "result": result}
    else:
        return {"error": f"Unsupported operation: '{operation}'. Please use 'sum' or 'multiply'."}