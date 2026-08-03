"""
Lab 05 — Deploy Agent on AgentCore Runtime
Day 1: Breakout Lab

TODO: Complete the deployment configuration and deploy your agent.

The instructor has pre-created:
- AgentCore Gateway (read-only tool target)
- AgentCore Memory resource
- IAM execution role shell with trust policy
- Log groups and identity configuration

You will:
1. Fill in the execution role ARN (provided by instructor)
2. Configure the deployment parameters
3. Deploy the agent to AgentCore Runtime
"""
import json
import os
import uuid

import boto3

# --- Configuration (fill in from your sandbox) ---
# TODO: Replace with the execution role ARN from your instructor
EXECUTION_ROLE_ARN = os.environ.get(
    "EXECUTION_ROLE_ARN",
    "arn:aws:iam::123456789012:role/ProdAgentRole",  # ← REPLACE ME
)

# TODO: Replace with your S3 bucket for agent code artifacts
S3_BUCKET = os.environ.get(
    "S3_BUCKET",
    "agentcore-artifacts-demo",  # ← REPLACE ME
)

# TODO: Set your unique agent name (use your team prefix)
AGENT_NAME = os.environ.get(
    "AGENT_NAME",
    "LabAgent-Team01",  # ← REPLACE ME with your team prefix
)

# AWS region for your sandbox
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Initialize the control plane client
control = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)


def deploy():
    """Deploy the agent to AgentCore Runtime.

    This creates a new Runtime endpoint with:
    - Your agent code (packaged as a zip in S3)
    - A least-privilege IAM execution role
    - Lifecycle controls (idle timeout, max lifetime)
    - Network configuration (PUBLIC mode for classroom)
    """
    print("=" * 60)
    print("  Deploying AgentCore Agent")
    print("=" * 60)
    print(f"  Agent Name: {AGENT_NAME}")
    print(f"  Role ARN:   {EXECUTION_ROLE_ARN}")
    print(f"  Region:     {AWS_REGION}")
    print()

    # Build the deployment parameters
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
            "idleRuntimeSessionTimeout": 300,  # 5 min idle timeout
            "maxLifetime": 28800,  # 8 hours max
        },
        "clientToken": str(uuid.uuid4()),
    }

    print("  Deployment configuration:")
    print(f"  {json.dumps(params, indent=4)}")
    print()

    # TODO: Uncomment the line below to actually deploy
    # response = control.create_agent_runtime(**params)
    # agent_arn = response["agentRuntimeArn"]
    # print(f"\n  Agent deployed successfully!")
    # print(f"  Runtime ARN: {agent_arn}")
    # return agent_arn

    print("  [Simulated] Agent deployed successfully.")
    print(f"  Runtime ARN: arn:aws:bedrock-agentcore:{AWS_REGION}:123456789012:agent-runtime/{AGENT_NAME}")
    print()
    print("  Next step: Run verify_memory.py to test your agent.")
    return f"arn:aws:bedrock-agentcore:{AWS_REGION}:123456789012:agent-runtime/{AGENT_NAME}"


if __name__ == "__main__":
    deploy()
