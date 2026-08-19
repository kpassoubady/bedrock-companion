"""
Lab 05 - Governed agent for the Salesforce case + retail order-status scenario.

Deployed to AgentCore Runtime as a direct-code Python ZIP (entryPoint agent.py).
Implements the Runtime HTTP contract directly (no bedrock-agentcore SDK):
  GET  /ping          health check
  POST /invocations   {"prompt": ..., "actorId": ..., "memorySessionId": ...}

On each invocation the agent:
  1. Loads prior conversation turns for this actorId/memorySessionId from
     AgentCore Memory, so a second, different Runtime session can recall
     what an earlier session was told.
  2. Asks the model to answer the prompt, offering the read-only Gateway
     order-status tool.
  3. Calls the Gateway over MCP (SigV4-signed with the Runtime's own
     execution role) whenever the model asks for the tool.
  4. Writes both the user prompt and the final answer back to Memory.
"""
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import urllib.request

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "")
GATEWAY_TOOL_NAME = os.environ.get("GATEWAY_TOOL_NAME", "")
MEMORY_ID = os.environ.get("MEMORY_ID", "")
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")

SYSTEM_PROMPT = (
    "You help with two kinds of requests: checking a retail order's status "
    "using the order_status tool, and remembering short facts the user tells "
    "you (such as a Salesforce case number) so you can recall them later in "
    "a different conversation. Always call order_status instead of guessing "
    "a status. When asked to recall something, answer only from the "
    "conversation history provided to you."
)

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "order_status",
                "description": "Look up the status of a retail order.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "orderId": {
                                "type": "string",
                                "description": "The order identifier to look up, e.g. ORD-1001",
                            }
                        },
                        "required": ["orderId"],
                    }
                },
            }
        }
    ]
}

_bedrock = None
_agentcore = None


def bedrock_client():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return _bedrock


def agentcore_client():
    global _agentcore
    if _agentcore is None:
        _agentcore = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
    return _agentcore


def call_gateway_tool(order_id: str) -> str:
    """Invoke the Gateway's order-status MCP tool with the Runtime's own SigV4 identity."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {"name": GATEWAY_TOOL_NAME, "arguments": {"orderId": order_id}},
    }
    body = json.dumps(payload).encode("utf-8")
    credentials = boto3.Session(region_name=AWS_REGION).get_credentials()
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
    urllib_request = urllib.request.Request(
        GATEWAY_URL, data=body, headers=dict(request.headers.items()), method="POST"
    )
    with urllib.request.urlopen(urllib_request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
    if "error" in result:
        return json.dumps({"error": result["error"]})
    content = result.get("result", {}).get("content", [])
    texts = [item["text"] for item in content if item.get("type") == "text"]
    return "\n".join(texts) if texts else json.dumps(result.get("result", {}))


def load_memory_turns(actor_id: str, session_id: str):
    """Return prior conversation turns for this actor/session as Converse messages."""
    if not MEMORY_ID:
        return []
    response = agentcore_client().list_events(
        memoryId=MEMORY_ID,
        actorId=actor_id,
        sessionId=session_id,
        includePayloads=True,
        maxResults=100,
    )
    events = sorted(response.get("events", []), key=lambda e: e.get("eventTimestamp", 0))
    messages = []
    for event in events:
        for item in event.get("payload", []):
            turn = item.get("conversational")
            if not turn:
                continue
            text = turn.get("content", {}).get("text", "")
            role = turn.get("role", "USER")
            if not text:
                continue
            messages.append({"role": "user" if role == "USER" else "assistant", "content": [{"text": text}]})
    return messages


def write_memory_turn(actor_id: str, session_id: str, role: str, text: str) -> None:
    if not MEMORY_ID:
        return
    agentcore_client().create_event(
        memoryId=MEMORY_ID,
        actorId=actor_id,
        sessionId=session_id,
        eventTimestamp=time.time(),
        payload=[{"conversational": {"content": {"text": text}, "role": role}}],
    )


def run_conversation(prompt: str, history: list) -> str:
    messages = history + [{"role": "user", "content": [{"text": prompt}]}]

    for _ in range(4):
        response = bedrock_client().converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            toolConfig=TOOL_CONFIG,
        )
        output_message = response["output"]["message"]
        messages.append(output_message)

        if response.get("stopReason") != "tool_use":
            return "".join(block.get("text", "") for block in output_message["content"])

        tool_results = []
        for block in output_message["content"]:
            tool_use = block.get("toolUse")
            if not tool_use:
                continue
            if tool_use["name"] == "order_status":
                result_text = call_gateway_tool(tool_use["input"]["orderId"])
            else:
                result_text = json.dumps({"error": f"unknown tool {tool_use['name']}"})
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tool_use["toolUseId"],
                        "content": [{"text": result_text}],
                    }
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "I could not complete that request."


def handle_invocation(body: dict) -> dict:
    prompt = body.get("prompt", "")
    actor_id = body.get("actorId", "")
    session_id = body.get("memorySessionId", "")

    history = load_memory_turns(actor_id, session_id)
    answer = run_conversation(prompt, history)

    write_memory_turn(actor_id, session_id, "USER", prompt)
    write_memory_turn(actor_id, session_id, "ASSISTANT", answer)

    return {"response": answer}


class Handler(BaseHTTPRequestHandler):
    def _write_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/ping":
            self._write_json(200, {"status": "Healthy"})
            return
        self._write_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/invocations":
            self._write_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
            result = handle_invocation(body)
            self._write_json(200, result)
        except Exception as e:
            print(f"INVOCATION_ERROR: {e}", file=sys.stderr, flush=True)
            self._write_json(500, {"error": str(e)})

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}", flush=True)


def main():
    print("AGENT_STARTING: binding 0.0.0.0:8080", flush=True)
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("AGENT_READY: listening on 0.0.0.0:8080", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
