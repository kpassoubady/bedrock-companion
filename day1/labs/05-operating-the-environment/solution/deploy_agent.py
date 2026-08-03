"""
Lab 05 — Solution: Deploy Agent on AgentCore Runtime
Day 1: Breakout Lab

Complete working example. Deploys an agent to AgentCore Runtime with
least-privilege IAM, lifecycle controls, and network configuration.
"""
import json
import os
import uuid

import boto3

# --- Configuration ---
EXECUTION_ROLE_ARN = os.environ.get(
    "EXECUTION_ROLE_ARN",
    "arn:aws:iam::123456789012:role/ProdAgentRole",
)
S3_BUCKET = os.environ.get("S3_BUCKET", "agentcore-artifacts-demo")
AGENT_NAME = os.environ.get("AGENT_NAME", "LabAgent-Team01")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

control = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)


def deploy():
    """Deploy the agent to AgentCore Runtime.

    Creates a Runtime endpoint with code deployment from S3,
    a scoped IAM execution role, and lifecycle cost controls.
    """
    print("=" * 60)
    print("  Deploying AgentCore Agent")
    print("=" * 60)
    print(f"  Agent Name: {AGENT_NAME}")
    print(f"  Role ARN:   {EXECUTION_ROLE_ARN}")
    print(f"  S3 Bucket:  {S3_BUCKET}")
    print(f"  Region:     {AWS_REGION}")
    print()

    params = {
        "agentRuntimeName": AGENT_NAME,
        "agentRuntimeArtifact": {
            "codeConfiguration": {
                "code": {
                    "s3": {
                        "bucket": S3_BUCKET,
                        "prefix": f"{AGENT_NAME}/v1",
                    }
                },
                "runtime": "PYTHON_3_12",
                "entryPoint": ["agent.py"],
            }
        },
        "roleArn": EXECUTION_ROLE_ARN,
        "networkConfiguration": {
            "networkMode": "PUBLIC",
        },
        "description": f"Lab agent for {AGENT_NAME} — Day 1 breakout",
        "lifecycleConfiguration": {
            "idleRuntimeSessionTimeout": 300,
            "maxLifetime": 28800,
        },
        "clientToken": str(uuid.uuid4()),
    }

    print("  Deployment configuration:")
    print(f"  {json.dumps(params, indent=4)}")
    print()

    # Uncomment to deploy to AWS:
    # response = control.create_agent_runtime(**params)
    # agent_arn = response["agentRuntimeArn"]
    # print(f"  Agent deployed successfully!")
    # print(f"  Runtime ARN: {agent_arn}")
    # return agent_arn

    print("  [Simulated] Agent deployed successfully.")
    agent_arn = f"arn:aws:bedrock-agentcore:{AWS_REGION}:123456789012:agent-runtime/{AGENT_NAME}"
    print(f"  Runtime ARN: {agent_arn}")
    print()
    print("  Next step: Run verify_memory.py to test your agent.")
    return agent_arn


if __name__ == "__main__":
    deploy()
