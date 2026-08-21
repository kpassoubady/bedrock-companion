"""
Demo — AgentCore Gateway Governed Tool Access
Day 1 — Block 2: Core Execution (Runtime and Gateway)

Shows how AgentCore Gateway exposes approved tools through MCP targets by
deriving the MCP request/response chain from whatever order ID the agent
asks for, using a small local order table. Also evaluates a real IAM
`Condition` object against sample caller ARNs to show which callers a
Gateway-only Runtime resource policy would block.

No AWS credentials or network access required.
Run: python3 day1/demos/demo-gateway-tool-access.py
"""
import json
import os
import uuid

# --- Configuration ---
GATEWAY_NAME = os.environ.get("GATEWAY_NAME", "ProdGateway")
GATEWAY_ROLE_ARN = os.environ.get(
    "GATEWAY_ROLE_ARN",
    "arn:aws:iam::123456789012:role/AgentCoreGatewayRole",
)

# Local stand-in for the retail order target the Gateway would route to.
ORDER_STATUSES = {
    "ORD-555": "Shipped",
    "ORD-777": "Processing",
    "ORD-901": "Delivered",
}


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def create_gateway():
    """Create an AgentCore Gateway with MCP protocol support.
    This is the boto3 pattern for create_gateway."""
    print_section("Creating AgentCore Gateway")

    params = {
        "name": GATEWAY_NAME,
        "protocolType": "MCP",
        "protocolConfiguration": {
            "mcp": {
                "supportedVersions": ["2024-11-05", "2025-03-26"],
                "instructions": "Gateway for production agent tools",
                "sessionConfiguration": {
                    "sessionTimeoutInSeconds": 3600,
                },
            }
        },
        "authorizerType": "AWS_IAM",
        "roleArn": GATEWAY_ROLE_ARN,
        "clientToken": str(uuid.uuid4()),
    }

    print("  API: bedrock-agentcore-control.create_gateway")
    print(f"  Parameters:\n{json.dumps(params, indent=4)}")

    # In production, uncomment to actually deploy:
    # control = boto3.client("bedrock-agentcore-control")
    # response = control.create_gateway(**params)
    # print(f"  Created: {response['gatewayArn']}")

    print("\n  Preview complete. No Gateway or target was created.")
    return params


def gateway_mcp_translation(order_id: str = "ORD-555"):
    """Show how Gateway translates a tool call to MCP JSON-RPC and back.

    The response is derived from `order_id` through a local order table —
    changing the requested order changes every downstream value, unlike a
    fixed set of matching literal strings."""
    print_section(f"Gateway MCP Protocol Translation — order_id={order_id}")

    # Agent requests a tool in natural format
    agent_request = {
        "tool": "get_order_status",
        "parameters": {"order_id": order_id},
    }
    print(f"  Agent request: {json.dumps(agent_request)}")

    # Gateway translates to MCP JSON-RPC — arguments come straight from the request
    mcp_request = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4())[:8],
        "method": "tools/call",
        "params": {
            "name": agent_request["tool"],
            "arguments": agent_request["parameters"],
        },
    }
    print(f"\n  Gateway translates to MCP:\n  {json.dumps(mcp_request, indent=2)}")

    # Target looks up the real status for the requested order — no match, no answer.
    status = ORDER_STATUSES.get(order_id)
    is_error = status is None
    result_text = f"Order {order_id} is {status}." if status else f"Order {order_id} not found."
    mcp_response = {
        "jsonrpc": "2.0",
        "id": mcp_request["id"],
        "result": {
            "content": [{"type": "text", "text": result_text}],
            "isError": is_error,
        },
    }
    print(f"\n  Target response:\n  {json.dumps(mcp_response, indent=2)}")

    # Gateway translates back — status/output read from the target's own response.
    agent_response = {
        "tool": agent_request["tool"],
        "status": "error" if is_error else "success",
        "output": mcp_response["result"]["content"][0]["text"],
    }
    print(f"\n  Gateway translates back to agent:\n  {json.dumps(agent_response, indent=2)}")
    return agent_response


def gateway_vs_api_gateway():
    """Distinguish AgentCore Gateway from Amazon API Gateway.

    This is a key learning outcome: students must understand where each
    belongs in an enterprise architecture."""
    print_section("AgentCore Gateway vs. Amazon API Gateway")

    comparison = {
        "AgentCore Gateway": {
            "role": "Agent-facing tool routing",
            "protocol": "MCP (Model Context Protocol)",
            "functions": [
                "Tool discovery and invocation",
                "Protocol translation (REST→MCP, Lambda→MCP)",
                "Tool allowlisting and governance",
                "Agent-to-agent communication (A2A)",
            ],
        },
        "Amazon API Gateway": {
            "role": "Client-facing API edge",
            "protocol": "HTTP/REST/WebSocket",
            "functions": [
                "Client authentication (Cognito, Okta, etc.)",
                "Throttling and rate limiting",
                "WAF integration and DDoS protection",
                "Request/response transformation",
                "API versioning and canary deployment",
            ],
        },
    }
    print(f"  {json.dumps(comparison, indent=2)}")
    print("\n  Typical enterprise flow:")
    print("  Client → API Gateway (auth, throttle) → Backend → AgentCore Runtime → AgentCore Gateway → Tools")


def evaluate_gateway_only_condition(caller_arn: str) -> bool:
    """Evaluate a real IAM Deny condition: is this caller blocked from
    invoking Runtime directly (i.e., is it anything but the Gateway role)?

    Mirrors a `Deny` statement with `StringNotEquals` on `aws:PrincipalArn`.
    Returns True if the condition matches and the call would be denied."""
    condition = {
        "Sid": "EnforceGatewayOnlyAccess",
        "Effect": "Deny",
        "Action": "bedrock-agentcore:InvokeAgentRuntime",
        "Resource": "*",
        "Condition": {
            "StringNotEquals": {
                "aws:PrincipalArn": GATEWAY_ROLE_ARN,
            },
        },
    }
    denied = caller_arn != condition["Condition"]["StringNotEquals"]["aws:PrincipalArn"]
    return condition, denied


def direct_bypass_prevention():
    """Evaluate the Gateway-only IAM condition against real sample callers,
    instead of only narrating that a condition exists."""
    print_section("Direct Bypass Prevention — IAM Condition Evaluation")

    sample_callers = {
        "Approved Gateway role": GATEWAY_ROLE_ARN,
        "Rogue caller with a valid signature": "arn:aws:iam::123456789012:role/SomeOtherService",
    }

    condition = None
    for label, caller_arn in sample_callers.items():
        condition, denied = evaluate_gateway_only_condition(caller_arn)
        verdict = "DENIED" if denied else "ALLOWED"
        print(f"  {label}:")
        print(f"    Caller ARN: {caller_arn}")
        print(f"    Verdict:    {verdict}")

    print(f"\n  Condition object evaluated above:\n  {json.dumps(condition, indent=2)}")
    print()
    print("  Normal flow:")
    print("  - The approved backend invokes Runtime")
    print("  - Runtime invokes AgentCore Gateway for approved tools")
    print("  - Gateway authorizes the caller and target invocation")
    print("  - The downstream service re-checks business authorization")
    print()
    print("  Gateway does not replace Runtime ingress authorization or downstream checks.")


def main():
    print("AgentCore Gateway — Governed Tool Access Demo")
    print(f"Gateway: {GATEWAY_NAME}\n")

    create_gateway()
    gateway_mcp_translation("ORD-555")
    gateway_mcp_translation("ORD-404")  # not in ORDER_STATUSES — shows the error path
    gateway_vs_api_gateway()
    direct_bypass_prevention()

    print_section("Key Takeaways")
    print("  1. Gateway is agent-facing and tool-aware — it does not replace API Gateway")
    print("  2. MCP protocol standardizes how agents discover and invoke tools")
    print("  3. The target's response — and any errors — are derived from the actual request")
    print("  4. A Gateway-only IAM condition denies any caller that isn't the Gateway role")
    print("  5. Downstream services must still re-verify authorization per request")


if __name__ == "__main__":
    main()
