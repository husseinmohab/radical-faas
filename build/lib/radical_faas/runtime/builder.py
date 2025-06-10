"""
Builds user source code into a runnable container image.

This module uses the Docker SDK to dynamically create a Dockerfile,
build an image containing the user's function and a wrapper, and
push it to a container registry.
"""

import docker
import os
import tempfile
import shutil
import json

from ..api import schemas
from ..config import settings


# This executor script runs inside the container and executes the user's code.
WRAPPER_SCRIPT = """
import os
import json
import importlib

def run():
    payload_str = os.environ.get("RADICAL_PAYLOAD", "{}")
    handler_str = os.environ.get("RADICAL_HANDLER", "main.handle")

    try:
        payload = json.loads(payload_str)
        module_name, function_name = handler_str.split('.')
        
        print(f"Wrapper: Importing '{function_name}' from '{module_name}.py'...")
        user_module = importlib.import_module(module_name)
        handler_func = getattr(user_module, function_name)

        print(f"Wrapper: Executing function with payload: {payload}")
        result = handler_func(payload)

        print("---RESULT_START---")
        print(json.dumps(result))
        print("---RESULT_END---")

    except Exception as e:
        print(f"Wrapper Error: {e}")
        exit(1)

if __name__ == "__main__":
    run()
"""


async def build_image_from_code(function_data: schemas.FunctionCreate) -> str:
    """
    Creates a container image from function source code.

    Args:
        function_data: The function's metadata, including source code.

    Returns:
        The URI of the newly built and pushed container image.
    """
    client = docker.from_env()
    image_uri = f"{settings.container_registry}/{function_data.name}:latest"
    build_path = tempfile.mkdtemp()
    print(f"Builder: Created temporary build context at {build_path}")

    try:
        module_name, _ = function_data.handler.split('.')
        with open(os.path.join(build_path, f"{module_name}.py"), "w") as f:
            f.write(function_data.code)

        with open(os.path.join(build_path, "wrapper.py"), "w") as f:
            f.write(WRAPPER_SCRIPT)

        dockerfile_content = f"""
        FROM {function_data.runtime}
        WORKDIR /app
        COPY . .
        CMD ["python", "wrapper.py"]
        """
        with open(os.path.join(build_path, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)

        print(f"Builder: Building image '{image_uri}'...")
        client.images.build(path=build_path, tag=image_uri, rm=True)
        
        # Uncomment the following lines to push to a real registry
        # print(f"Builder: Pushing image '{image_uri}'...")
        # for line in client.images.push(image_uri, stream=True, decode=True):
        #     print(line)

    finally:
        print(f"Builder: Cleaning up build context at {build_path}")
        shutil.rmtree(build_path)

    return image_uri