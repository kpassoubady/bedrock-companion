"""
Lab 05 - Deploy or update an AgentCore Runtime.

Set the instructor-provided environment variables, then run:
python3 deploy_agent.py
"""
import os
import re
import time
import uuid

import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AGENT_NAME = os.environ.get("AGENT_NAME", "")
AGENT_RUNTIME_ID = os.environ.get("AGENT_RUNTIME_ID", "")
EXECUTION_ROLE_ARN = os.environ.get("EXECUTION_ROLE_ARN", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_KEY = os.environ.get("S3_KEY", "")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "")
GATEWAY_TOOL_NAME = os.environ.get("GATEWAY_TOOL_NAME", "")
MEMORY_ID = os.environ.get("MEMORY_ID", "")


def require_configuration():
    required = {
        "AGENT_NAME": AGENT_NAME,
        "EXECUTION_ROLE_ARN": EXECUTION_ROLE_ARN,
        "S3_BUCKET": S3_BUCKET,
        "S3_KEY": S3_KEY,
        "GATEWAY_URL": GATEWAY_URL,
        "GATEWAY_TOOL_NAME": GATEWAY_TOOL_NAME,
        "MEMORY_ID": MEMORY_ID,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise SystemExit(f"CONFIG_MISSING: export {', '.join(missing)}")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,47}", AGENT_NAME):
        raise SystemExit("CONFIG_INVALID: AGENT_NAME must start with a letter and contain only letters, digits, or underscores")
    if not S3_KEY.endswith(".zip"):
        raise SystemExit("CONFIG_INVALID: S3_KEY must identify the direct-deployment ZIP object")


def runtime_configuration():
    return {
        "agentRuntimeArtifact": {
            "codeConfiguration": {
                "code": {"s3": {"bucket": S3_BUCKET, "prefix": S3_KEY}},
                "runtime": "PYTHON_3_12",
                "entryPoint": ["agent.py"],
            }
        },
        "roleArn": EXECUTION_ROLE_ARN,
        "networkConfiguration": {"networkMode": "PUBLIC"},
        "description": f"AgentCore course Runtime for {AGENT_NAME}",
        "lifecycleConfiguration": {
            "idleRuntimeSessionTimeout": 300,
            "maxLifetime": 28800,
        },
        "environmentVariables": {
            "COURSE_SCENARIO": "salesforce-case-and-retail-order",
            "AWS_REGION": AWS_REGION,
            "GATEWAY_URL": GATEWAY_URL,
            "GATEWAY_TOOL_NAME": GATEWAY_TOOL_NAME,
            "MEMORY_ID": MEMORY_ID,
        },
    }


def find_runtime_by_name(control, name: str):
    """Return the existing Runtime dict with this name, or None."""
    paginator = control.get_paginator("list_agent_runtimes")
    for page in paginator.paginate():
        for runtime in page.get("agentRuntimes", []):
            if runtime.get("agentRuntimeName") == name:
                return runtime
    return None


def wait_until_ready(control, runtime_id: str, version: str):
    deadline = time.time() + 300
    while time.time() < deadline:
        runtime = control.get_agent_runtime(
            agentRuntimeId=runtime_id,
            agentRuntimeVersion=version,
        )
        status = runtime["status"]
        print(f"DEPLOYMENT_WAIT: status={status}")
        if status == "READY":
            return runtime
        if status in {"CREATE_FAILED", "UPDATE_FAILED"}:
            raise SystemExit(f"DEPLOYMENT_FAILED: {runtime.get('failureReason', status)}")
        time.sleep(10)
    raise SystemExit("DEPLOYMENT_TIMEOUT: Runtime did not become READY within five minutes")


def create_runtime(control, configuration):
    print(f"DEPLOYMENT_START: creating Runtime {AGENT_NAME}")
    return control.create_agent_runtime(
        agentRuntimeName=AGENT_NAME,
        clientToken=str(uuid.uuid4()),
        **configuration,
    )


def wait_until_deleted(control, runtime_id: str, name: str):
    deadline = time.time() + 120
    while time.time() < deadline:
        if find_runtime_by_name(control, name) is None:
            return
        print(f"DEPLOYMENT_WAIT: waiting for Runtime {runtime_id} to finish deleting")
        time.sleep(5)
    raise SystemExit(
        f"DEPLOYMENT_TIMEOUT: Runtime {runtime_id} did not finish deleting within two minutes"
    )


def deploy():
    require_configuration()
    session = boto3.Session(region_name=AWS_REGION)
    session.client("s3").head_object(Bucket=S3_BUCKET, Key=S3_KEY)
    control = session.client("bedrock-agentcore-control")
    configuration = runtime_configuration()

    runtime_id = AGENT_RUNTIME_ID
    if not runtime_id:
        existing = find_runtime_by_name(control, AGENT_NAME)
        if existing:
            runtime_id = existing["agentRuntimeId"]
            print(f"DEPLOYMENT_INFO: found existing Runtime {runtime_id} named {AGENT_NAME}")

    if runtime_id:
        print(f"DEPLOYMENT_START: updating Runtime {runtime_id}")
        response = control.update_agent_runtime(
            agentRuntimeId=runtime_id,
            **configuration,
        )
    else:
        try:
            response = create_runtime(control, configuration)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConflictException":
                raise
            # Name collision with no discoverable match (e.g. propagation lag,
            # or a Runtime left over from an interrupted run) — clear it and
            # retry once rather than forcing a manual delete every time.
            conflicting = find_runtime_by_name(control, AGENT_NAME)
            if not conflicting:
                raise
            print(
                f"DEPLOYMENT_INFO: deleting conflicting Runtime "
                f"{conflicting['agentRuntimeId']} named {AGENT_NAME}"
            )
            control.delete_agent_runtime(agentRuntimeId=conflicting["agentRuntimeId"])
            wait_until_deleted(control, conflicting["agentRuntimeId"], AGENT_NAME)
            response = create_runtime(control, configuration)

    runtime = wait_until_ready(
        control,
        response["agentRuntimeId"],
        response["agentRuntimeVersion"],
    )
    print("DEPLOYMENT_OK")
    print(f"AGENT_RUNTIME_ID={runtime['agentRuntimeId']}")
    print(f"AGENT_RUNTIME_VERSION={runtime['agentRuntimeVersion']}")
    print(f"AGENT_RUNTIME_ARN={runtime['agentRuntimeArn']}")
    write_deploy_env(runtime)
    return runtime


def write_deploy_env(runtime):
    """
    Write deploy.env with this run's Runtime identifiers so later checkpoints
    (verify_memory.py, etc.) can `source deploy.env` instead of copy-pasting
    values printed to the terminal.
    """
    path = os.path.join(os.getcwd(), "deploy.env")
    with open(path, "w") as f:
        f.write(f"export AGENT_RUNTIME_ID={runtime['agentRuntimeId']}\n")
        f.write(f"export AGENT_RUNTIME_VERSION={runtime['agentRuntimeVersion']}\n")
        f.write(f"export AGENT_RUNTIME_ARN={runtime['agentRuntimeArn']}\n")
    print(f"DEPLOYMENT_INFO: wrote {path} — run `source deploy.env` to load these into your shell")


if __name__ == "__main__":
    deploy()
