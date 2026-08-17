"""
Lab 05 - Invoke a pre-created AgentCore Gateway tool with IAM SigV4.

Run: python3 check_gateway.py
"""
import json
import os
import urllib.error
import urllib.request
import uuid

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "")
GATEWAY_TOOL_NAME = os.environ.get("GATEWAY_TOOL_NAME", "")
ORDER_ID = os.environ.get("ORDER_ID", "ORD-1001")
EXPECTED_ORDER_STATUS = os.environ.get("EXPECTED_ORDER_STATUS", "SHIPPED")


def require_configuration():
    missing = [name for name, value in {
        "GATEWAY_URL": GATEWAY_URL,
        "GATEWAY_TOOL_NAME": GATEWAY_TOOL_NAME,
    }.items() if not value]
    if missing:
        raise SystemExit(f"CONFIG_MISSING: export {', '.join(missing)}")
    if not GATEWAY_URL.startswith("https://"):
        raise SystemExit("CONFIG_INVALID: GATEWAY_URL must use HTTPS")


def signed_headers(body: bytes):
    credentials = boto3.Session(region_name=AWS_REGION).get_credentials()
    if credentials is None:
        raise SystemExit("IAM_FAILED: no AWS credentials are available")
    request = AWSRequest(
        method="POST",
        url=GATEWAY_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "MCP-Protocol-Version": "2025-03-26",
        },
    )
    SigV4Auth(credentials.get_frozen_credentials(), "bedrock-agentcore", AWS_REGION).add_auth(request)
    return dict(request.headers.items())


def main():
    require_configuration()
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": GATEWAY_TOOL_NAME,
            "arguments": {"orderId": ORDER_ID},
        },
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        GATEWAY_URL,
        data=body,
        headers=signed_headers(body),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GATEWAY_FAILED: HTTP {error.code}: {detail}") from error

    if result.get("id") != payload["id"]:
        raise SystemExit("GATEWAY_FAILED: JSON-RPC response ID did not match the request")
    if "error" in result:
        raise SystemExit(f"GATEWAY_FAILED: {json.dumps(result['error'])}")
    tool_result = result.get("result")
    if not isinstance(tool_result, dict):
        raise SystemExit("GATEWAY_FAILED: response did not contain a JSON-RPC result object")
    if tool_result.get("isError") is True:
        raise SystemExit(f"GATEWAY_FAILED: tool returned isError=true: {json.dumps(tool_result)}")
    serialized = json.dumps(tool_result, sort_keys=True)
    if ORDER_ID.lower() not in serialized.lower():
        raise SystemExit(f"GATEWAY_FAILED: response did not contain expected order ID {ORDER_ID}")
    if EXPECTED_ORDER_STATUS.lower() not in serialized.lower():
        raise SystemExit(f"GATEWAY_FAILED: response did not contain expected status {EXPECTED_ORDER_STATUS}")
    print("GATEWAY_OK")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
