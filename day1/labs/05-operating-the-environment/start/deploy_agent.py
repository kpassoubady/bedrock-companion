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

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AGENT_NAME = os.environ.get("AGENT_NAME", "")
AGENT_RUNTIME_ID = os.environ.get("AGENT_RUNTIME_ID", "")
EXECUTION_ROLE_ARN = os.environ.get("EXECUTION_ROLE_ARN", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_KEY = os.environ.get("S3_KEY", "")


def require_configuration():
    required = {
        "AGENT_NAME": AGENT_NAME,
        "EXECUTION_ROLE_ARN": EXECUTION_ROLE_ARN,
        "S3_BUCKET": S3_BUCKET,
        "S3_KEY": S3_KEY,
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
        },
    }


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


def deploy():
    require_configuration()
    session = boto3.Session(region_name=AWS_REGION)
    session.client("s3").head_object(Bucket=S3_BUCKET, Key=S3_KEY)
    control = session.client("bedrock-agentcore-control")
    configuration = runtime_configuration()

    if AGENT_RUNTIME_ID:
        print(f"DEPLOYMENT_START: updating Runtime {AGENT_RUNTIME_ID}")
        response = control.update_agent_runtime(
            agentRuntimeId=AGENT_RUNTIME_ID,
            **configuration,
        )
    else:
        print(f"DEPLOYMENT_START: creating Runtime {AGENT_NAME}")
        response = control.create_agent_runtime(
            agentRuntimeName=AGENT_NAME,
            clientToken=str(uuid.uuid4()),
            **configuration,
        )

    runtime = wait_until_ready(
        control,
        response["agentRuntimeId"],
        response["agentRuntimeVersion"],
    )
    print("DEPLOYMENT_OK")
    print(f"AGENT_RUNTIME_ID={runtime['agentRuntimeId']}")
    print(f"AGENT_RUNTIME_VERSION={runtime['agentRuntimeVersion']}")
    print(f"AGENT_RUNTIME_ARN={runtime['agentRuntimeArn']}")
    return runtime


if __name__ == "__main__":
    deploy()
