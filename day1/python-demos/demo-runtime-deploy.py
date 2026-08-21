"""
Demo — AgentCore Runtime Deployment
Day 1 — Block 2: Core Execution (Runtime and Gateway)

Builds a real create_agent_runtime request and validates it against the
CreateAgentRuntime request shape from the installed boto3 service model
using botocore.validate.validate_parameters. Validation runs entirely
offline: it inspects the local service model, makes no network call, and
needs no AWS credentials. The demo does not create a Runtime — live
deployment is reserved for the lab, where students use a prebuilt ZIP,
execution role, and assigned S3 bucket.

Requires boto3 (already in the course stack). No AWS credentials or
network access are used.
Run: python3 day1/demos/demo-runtime-deploy.py
"""
import json
import os
import uuid

try:
    import boto3
    import botocore.validate
    from botocore.exceptions import ParamValidationError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

# --- Configuration ---
AGENT_NAME = os.environ.get("AGENT_NAME", "SalesforceCaseDemo")
ROLE_ARN = os.environ.get(
    "EXECUTION_ROLE_ARN",
    "arn:aws:iam::123456789012:role/ProdAgentRole",
)
S3_BUCKET = os.environ.get("S3_BUCKET", "agentcore-artifacts-demo")
S3_PREFIX = os.environ.get("S3_KEY", "salesforce-case-agent/deployment_package.zip")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def build_request_params() -> dict:
    return {
        "agentRuntimeName": AGENT_NAME,
        "agentRuntimeArtifact": {
            "codeConfiguration": {
                "code": {
                    "s3": {
                        "bucket": S3_BUCKET,
                        "prefix": S3_PREFIX,
                    }
                },
                "runtime": "PYTHON_3_12",
                "entryPoint": ["agent.py"],
            }
        },
        "roleArn": ROLE_ARN,
        "networkConfiguration": {
            "networkMode": "PUBLIC",
        },
        "description": "Salesforce case assistant classroom configuration",
        "lifecycleConfiguration": {
            "idleRuntimeSessionTimeout": 300,  # 5 min idle timeout
            "maxLifetime": 28800,  # 8 hours max
        },
        "clientToken": str(uuid.uuid4()),
    }


def validate_against_service_model(params: dict) -> bool:
    """Validate params against the real CreateAgentRuntime request shape.

    Constructing a boto3 client and reading its service model does not
    require credentials; botocore.validate.validate_parameters checks the
    shape locally and never makes a network call."""
    if not HAS_BOTO3:
        print("  boto3 is not installed — skipping live shape validation.")
        print("  Install with `pip3 install boto3` to run a real validation.")
        return False

    control = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)
    operation_model = control.meta.service_model.operation_model("CreateAgentRuntime")
    try:
        botocore.validate.validate_parameters(params, operation_model.input_shape)
        print("  Validation: PASS — params match the CreateAgentRuntime request shape")
        print(f"  (checked against botocore {botocore.__version__}'s bedrock-agentcore-control model)")
        return True
    except ParamValidationError as exc:
        print(f"  Validation: FAIL — {exc}")
        return False


def create_agent_runtime():
    """Build and validate a create_agent_runtime request.

    In the classroom, students use a pre-supplied script to actually
    deploy — this demo shows the instructor a real, shape-checked request."""
    print_section("Creating AgentCore Runtime")

    params = build_request_params()
    print("  API: bedrock-agentcore-control.create_agent_runtime")
    print(f"  Parameters:\n{json.dumps(params, indent=4)}")
    print()
    validate_against_service_model(params)

    print("\n  No AWS resource was created — validation is local and read-only.")
    print("  A live call returns a service-generated Runtime ARN and version.")
    return params


def show_update_pattern():
    """Distinguish classroom updates from staged production promotion."""
    print_section("Updating AgentCore Runtime")

    print("  update_agent_runtime creates a version and moves DEFAULT to it automatically.")
    print("  The classroom uses that direct update only in an isolated assigned sandbox.")
    print()
    print("  Staged production pattern:")
    print("  1. Keep the serving named endpoint pinned to the approved version")
    print("  2. Deploy the candidate version and test it through a separate endpoint or qualifier")
    print("  3. Run evaluation and operational checks")
    print("  4. Call update_agent_runtime_endpoint to promote the approved version")
    print("  Existing sessions can continue on the code version with which they started.")


def show_lifecycle_config():
    """Show lifecycle configuration parameters that prevent runaway costs."""
    print_section("Lifecycle Configuration — Cost Controls")

    runtime_config = {
        "idleRuntimeSessionTimeout": 300,
        "maxLifetime": 28800,
    }
    application_controls = {
        "max_iterations": 50,
        "request_deadline_seconds": 600,
        "stop_runtime_session": "Call proactively when the task completes",
    }
    print(f"  Runtime API fields:\n{json.dumps(runtime_config, indent=2)}")
    print(f"  Application or harness controls:\n{json.dumps(application_controls, indent=2)}")
    print("  maxLifetime replaces compute after eight hours; it is not a logical session cap.")


def main():
    print("AgentCore Runtime Deployment — Instructor Demo")
    print(f"Agent: {AGENT_NAME}")
    print(f"Role:  {ROLE_ARN}\n")

    create_agent_runtime()
    show_update_pattern()
    show_lifecycle_config()

    print_section("Key Takeaways")
    print("  1. Runtime hosts agent code in isolated microVMs per session")
    print("  2. Execution role must follow least privilege (never bedrock:*)")
    print("  3. Lifecycle configs are infrastructure controls, not prompts")
    print("  4. Immutable versions enable safe rollback")
    print("  5. Session isolation != tenant isolation — app owns user→session mapping")


if __name__ == "__main__":
    main()
