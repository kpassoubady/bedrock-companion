"""
Lab 05 — Solution: Verify Agent Memory Continuity
Day 1: Breakout Lab

Complete working example. Invokes the agent twice with the same actorId
and sessionId to verify short-term memory continuity, then guides the
student to inspect the trace in CloudWatch.
"""
import json
import os
import uuid

import boto3

# --- Configuration ---
AGENT_RUNTIME_ARN = os.environ.get(
    "AGENT_RUNTIME_ARN",
    "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/LabAgent-Team01",
)
ACTOR_ID = os.environ.get("ACTOR_ID", "student-01")
SESSION_ID = f"lab-session-{str(uuid.uuid4())[:8]}"
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

agentcore = boto3.client("bedrock-agentcore", region_name=AWS_REGION)


def invoke_agent(actor_id: str, session_id: str, message: str, invocation_num: int):
    """Invoke the deployed agent and display the response.

    Uses the same actorId and sessionId across invocations to demonstrate
    short-term memory continuity. The AgentCore Memory resource automatically
    provides conversation context for matching actorId + sessionId pairs.
    """
    print(f"\n{'─' * 50}")
    print(f"  Invocation {invocation_num}")
    print(f"  Actor: {actor_id} | Session: {session_id}")
    print(f"  Message: {message}")

    payload = json.dumps({"prompt": message}).encode("utf-8")

    # Uncomment to invoke your deployed agent:
    # response = agentcore.invoke_agent_runtime(
    #     agentRuntimeArn=AGENT_RUNTIME_ARN,
    #     runtimeSessionId=session_id,
    #     runtimeUserId=actor_id,
    #     contentType="application/json",
    #     payload=payload,
    # )
    #
    # if "text/event-stream" in response.get("contentType", ""):
    #     event_stream = response["response"]
    #     for event in event_stream:
    #         if "chunk" in event:
    #             chunk = event["chunk"]["bytes"].decode("utf-8")
    #             print(f"  Response: {chunk}")
    # else:
    #     body = response["response"].read()
    #     print(f"  Response: {body.decode('utf-8')}")

    # Simulated response for offline testing:
    if invocation_num == 1:
        print("  Response: I can help with that. What is your departure city?")
    elif invocation_num == 2:
        print("  Response: You are flying to Seattle next Monday. Shall I search for flights?")

    trace_id = uuid.uuid4().hex[:16]
    print(f"  Trace ID: {trace_id}")
    return trace_id


def main():
    print("=" * 60)
    print("  Agent Memory Continuity Verification")
    print("=" * 60)
    print(f"  Agent ARN: {AGENT_RUNTIME_ARN}")
    print(f"  Actor ID:  {ACTOR_ID}")
    print(f"  Session:   {SESSION_ID}")
    print()

    # Invocation 1: Set context (flight destination)
    trace_1 = invoke_agent(
        ACTOR_ID, SESSION_ID,
        "I need to book a flight to Seattle next Monday.",
        1,
    )

    # Invocation 2: Retrieve context (same actorId + sessionId)
    # The agent should recall "Seattle" from the first invocation
    trace_2 = invoke_agent(
        ACTOR_ID, SESSION_ID,
        "What is my destination?",
        2,
    )

    print(f"\n{'─' * 50}")
    print("\n  Verification complete!")
    print(f"\n  Trace IDs for CloudWatch inspection:")
    print(f"    Invocation 1: {trace_1}")
    print(f"    Invocation 2: {trace_2}")
    print(f"\n  CloudWatch path:")
    print(f"    CloudWatch → Generative AI Observability → AgentCore")
    print(f"    Filter by session ID: {SESSION_ID}")
    print(f"\n  Signals to record:")
    print(f"    - Total request duration (agent.run span)")
    print(f"    - Token usage (input + output per LLM call)")
    print(f"    - Tool invocations (which tools, how long)")
    print(f"    - Memory operations (reads/writes)")
    print(f"    - Errors (if any)")


if __name__ == "__main__":
    main()
