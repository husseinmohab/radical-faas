"""
The core orchestrator for RADICAL-FaaS, designed for Kubernetes.

This module translates FaaS-specific requests into Kubernetes resources,
letting Kubernetes handle the scheduling and execution.
"""

import json
import uuid
from kubernetes import client, config, watch
from typing import Dict, Any

from ..api import schemas
from ..runtime import builder
from ..store import metadata
from ..config import settings


def configure_kubernetes_client():
    """Loads Kubernetes configuration."""
    try:
        config.load_kube_config()
        print("Orchestrator: Loaded K8s config from kubeconfig file.")
    except config.ConfigException:
        config.load_incluster_config()
        print("Orchestrator: Loaded K8s config from in-cluster service account.")

configure_kubernetes_client()
core_v1_api = client.CoreV1Api()
batch_v1_api = client.BatchV1Api()


async def deploy_new_function(function_data: schemas.FunctionCreate) -> None:
    """Orchestrates the deployment of a new serverless function."""
    print(f"Orchestrator: Starting deployment for '{function_data.name}'.")
    image_uri = await builder.build_image_from_code(function_data)
    await metadata.save_function_details(
        name=function_data.name,
        image_uri=image_uri,
        handler=function_data.handler,
        runtime=function_data.runtime,
    )
    print(f"Orchestrator: Saved metadata for '{function_data.name}'.")


async def schedule_and_run_function(function_name: str, payload: dict) -> Dict[str, Any]:
    """Schedules and runs a function, then waits for and returns the result."""
    print(f"Orchestrator: Invoking '{function_name}'.")
    
    function_details = await metadata.get_function_details(function_name)
    if not function_details:
        raise ValueError(f"Function '{function_name}' not found.")

    image_uri = function_details["image_uri"]
    handler_str = function_details["handler"]
    job_name = f"{function_name}-{uuid.uuid4().hex[:6]}"

    container = client.V1Container(
        name=function_name,
        image=image_uri,
        env=[
            client.V1EnvVar(name="RADICAL_PAYLOAD", value=json.dumps(payload)),
            client.V1EnvVar(name="RADICAL_HANDLER", value=handler_str),
        ],
        image_pull_policy="IfNotPresent" # Important for local development
    )
    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"job-name": job_name}),
        spec=client.V1PodSpec(containers=[container], restart_policy="Never"),
    )
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            template=pod_template,
            backoff_limit=0,
            ttl_seconds_after_finished=settings.job_ttl_seconds_after_finished
        ),
    )

    batch_v1_api.create_namespaced_job(namespace=settings.job_namespace, body=job)
    print(f"Orchestrator: Submitted Job '{job_name}'. Monitoring for completion...")

    w = watch.Watch()
    for event in w.stream(
        batch_v1_api.list_namespaced_job,
        namespace=settings.job_namespace,
        field_selector=f"metadata.name={job_name}",
        timeout_seconds=120
    ):
        job_status = event['object'].status
        if job_status.succeeded:
            w.stop()
            print(f"Orchestrator: Job '{job_name}' succeeded.")
            pod_list = core_v1_api.list_namespaced_pod(
                namespace=settings.job_namespace,
                label_selector=f"job-name={job_name}"
            )
            pod_name = pod_list.items[0].metadata.name
            logs = core_v1_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=settings.job_namespace
            )
            try:
                result_str = logs.split("---RESULT_START---")[1].split("---RESULT_END---")[0]
                return json.loads(result_str.strip())
            except (IndexError, json.JSONDecodeError) as e:
                raise RuntimeError(f"Could not parse result from pod logs: {e}\nLogs: {logs}")
        elif job_status.failed:
            w.stop()
            raise RuntimeError(f"Job '{job_name}' failed.")
            
    raise TimeoutError(f"Job '{job_name}' did not complete in time.")