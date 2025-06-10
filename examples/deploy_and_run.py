"""An example client script to deploy and invoke a function on RADICAL-FaaS."""
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def deploy_calculator_function():
    """Deploys the sample calculator function from a file."""
    print("--- 1. Deploying Calculator Function ---")
    
    # Read the function code from the file
    with open("examples/sample_function.py", "r") as f:
        code_content = f.read()

    deploy_payload = {
        "name": "calculator",
        "runtime": "python:3.9-slim",
        "handler": "sample_function.handle",
        "code": code_content,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/functions", json=deploy_payload)
        response.raise_for_status()
        print("Deployment request successful:")
        print(json.dumps(response.json(), indent=2))
        # Give the builder some time to build the image
        time.sleep(15) 
    except requests.exceptions.RequestException as e:
        print(f"Error deploying function: {e}")
        exit(1)


def invoke_calculator_function():
    """Invokes the deployed calculator function with different payloads."""
    print("\n--- 2. Invoking with 'sum' operation ---")
    invoke_payload = {"payload": {"operation": "sum", "numbers": [10, 20, 30, 5]}}
    
    try:
        response = requests.post(f"{API_BASE_URL}/functions/calculator/invoke", json=invoke_payload)
        response.raise_for_status()
        print("Invocation successful:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error invoking function: {e}")

    print("\n--- 3. Invoking with 'multiply' operation ---")
    invoke_payload = {"payload": {"operation": "multiply", "numbers": [2, 3, 4]}}
    try:
        response = requests.post(f"{API_BASE_URL}/functions/calculator/invoke", json=invoke_payload)
        response.raise_for_status()
        print("Invocation successful:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error invoking function: {e}")

if __name__ == "__main__":
    deploy_calculator_function()
    invoke_calculator_function()