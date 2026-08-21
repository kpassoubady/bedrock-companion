"""
Lab 05 - Verify Runtime invocation and AgentCore Memory continuity.

The supplied Runtime must explicitly write and read AgentCore Memory using the
actorId and memorySessionId fields in the payload.
"""
import json
import os
import time
import uuid

import boto3

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
MEMORY_ID = os.environ.get("MEMORY_ID", "")
ACTOR_ID = os.environ.get("ACTOR_ID", f"actor-{uuid.uuid4()}")
MEMORY_SESSION_ID = os.environ.get("MEMORY_SESSION_ID", f"memory-{uuid.uuid4()}")
EXPECTED_TERM = os.environ.get("EXPECTED_TERM", "00001042")
ORDER_ID = os.environ.get("ORDER_ID", "ORD-1001")
EXPECTED_ORDER_STATUS = os.environ.get("EXPECTED_ORDER_STATUS", "SHIPPED")


def require_configuration():
    required = {
        "AGENT_RUNTIME_ARN": AGENT_RUNTIME_ARN,
        "MEMORY_ID": MEMORY_ID,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise SystemExit(f"CONFIG_MISSING: export {', '.join(missing)}")


def read_response(response):
    content_type = response.get("contentType", "")
    body = response["response"]
    if "text/event-stream" in content_type:
        chunks = []
        for raw_line in body.iter_lines(chunk_size=10):
            line = raw_line.decode("utf-8").strip()
            if line.startswith("data: "):
                chunks.append(line[6:])
        return "\n".join(chunks)
    raw = body.read().decode("utf-8")
    if content_type.startswith("application/json"):
        return json.dumps(json.loads(raw), sort_keys=True)
    return raw


def invoke(agentcore, prompt: str, runtime_session_id: str):
    payload = {
        "prompt": prompt,
        "actorId": ACTOR_ID,
        "memorySessionId": MEMORY_SESSION_ID,
    }
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=runtime_session_id,
        runtimeUserId=ACTOR_ID,
        contentType="application/json",
        accept="application/json, text/event-stream",
        payload=json.dumps(payload).encode("utf-8"),
    )
    text = read_response(response)
    request_id = response.get("ResponseMetadata", {}).get("RequestId", "unknown")
    print(f"RUNTIME_OK: request_id={request_id} runtime_session_id={runtime_session_id}")
    print(text)
    return text


def wait_for_memory_events(agentcore):
    deadline = time.time() + 30
    while time.time() < deadline:
        response = agentcore.list_events(
            memoryId=MEMORY_ID,
            actorId=ACTOR_ID,
            sessionId=MEMORY_SESSION_ID,
            includePayloads=True,
            maxResults=100,
        )
        events = response.get("events", [])
        if len(events) >= 2:
            return events
        time.sleep(3)
    raise SystemExit("MEMORY_FAILED: fewer than two events were visible after 30 seconds")


def main():
    require_configuration()
    agentcore = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
    first_runtime_session = f"runtime-{uuid.uuid4()}"
    second_runtime_session = f"runtime-{uuid.uuid4()}"

    first_response = invoke(
        agentcore,
        f"Check retail order {ORDER_ID} with the read-only tool and remember that Salesforce case {EXPECTED_TERM} concerns partner portal access.",
        first_runtime_session,
    )
    if ORDER_ID.lower() not in first_response.lower() or EXPECTED_ORDER_STATUS.lower() not in first_response.lower():
        raise SystemExit("TOOL_FAILED: Runtime response did not contain the expected order and status")
    print("TOOL_OK: Runtime invoked the expected read-only retail tool")
    second_response = invoke(
        agentcore,
        "Which Salesforce case did I ask you to remember?",
        second_runtime_session,
    )
    if EXPECTED_TERM not in second_response:
        raise SystemExit(f"CONTINUITY_FAILED: second response did not contain {EXPECTED_TERM}")

    events = wait_for_memory_events(agentcore)
    print(f"MEMORY_OK: actor_id={ACTOR_ID} memory_session_id={MEMORY_SESSION_ID} events={len(events)}")
    print("CONTINUITY_OK: different Runtime sessions retrieved the same Memory session")


if __name__ == "__main__":
    main()
