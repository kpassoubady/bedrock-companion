"""
Demo — AgentCore Request Lifecycle
Day 1 — Block 1: Welcome and Architecture Overview

Traces a Salesforce service-case request through five AgentCore focus
capabilities as an offline architecture walkthrough. Each step's elapsed
time is actually measured with time.perf_counter(), and the Gateway step
records a real tool-call entry — the closing trace's latency and
tool_calls values are computed from those measurements, not printed as
fixed literals.

No AWS credentials or API calls required.
Run: python3 day1/demos/demo-agentcore-lifecycle.py
"""
import json
import os
import time

# --- Configuration (set via environment or replace with your values) ---
AGENT_RUNTIME_ARN = os.environ.get(
    "AGENT_RUNTIME_ARN",
    "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/SalesforceCaseDemo-abcdefghij",
)
SESSION_ID = f"demo-session-{int(time.time())}"  # display label only; not used in any comparison or branch
ACTOR_ID = "instructor-demo"

# Filled in as the request actually moves through each step.
STEP_TIMINGS = {}
TOOL_CALLS = []


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def timed_step(name: str, fn, *args):
    """Run a step and record how long it actually took."""
    start = time.perf_counter()
    result = fn(*args)
    STEP_TIMINGS[name] = time.perf_counter() - start
    return result


def step_1_identity():
    """Caller identity is authenticated at the edge (API Gateway / BFF).
    AgentCore Identity propagates the caller context to Runtime."""
    print_section("1. Identity — Caller Authentication")
    print("  [Edge]  Authenticated caller via Amazon Cognito / Okta")
    print(f"  [Edge]  Caller ID: {ACTOR_ID}")
    print("  [Backend] Mapping the verified caller to an application-owned Runtime session")
    print("  [Identity] Workload identity: AgentCore Runtime execution role")
    return ACTOR_ID


def step_2_runtime(caller_id: str):
    """Runtime allocates an isolated microVM for the session.
    The agent code runs under a scoped IAM execution role."""
    print_section("2. Runtime — Session Isolation")
    print(f"  [Runtime] Starting or resuming isolated compute for session: {SESSION_ID}")
    print(f"  [Runtime] Runtime ARN: {AGENT_RUNTIME_ARN}")
    print(f"  [Runtime] Execution role: ProdAgentRole (least-privilege)")
    print(f"  [Runtime] Caller context: {caller_id}")
    print("  [Runtime] Session isolation separates compute; the app still maps tenant data")
    print("  NOTE: Application backend must map user → session ID")


def step_3_gateway():
    """Gateway routes the agent's tool call through governed, MCP-compatible
    endpoints. This walkthrough is offline; it records the call it narrates
    into TOOL_CALLS rather than claiming a live boto3 invocation."""
    print_section("3. Gateway — Governed Tool Access")
    print("  [Gateway] Agent requested tool: get_order_status")
    print("  [Gateway] Translating to MCP JSON-RPC protocol")
    print("  [Gateway] Validating tool allowlist and target authorization")
    print("  [Gateway] Routing to approved target (Lambda / HTTP)")
    print("  [Gateway] Response: Order ORD-555 is Shipped")
    print("  NOTE: Gateway is agent-facing; Amazon API Gateway handles client edge")
    TOOL_CALLS.append({"tool": "get_order_status", "status": "Success"})


def step_4_memory():
    """Memory stores and retrieves context scoped by actorId and sessionId.
    This is an offline walkthrough of the Memory API shape, not a live call —
    the lab's verify_memory.py exercises the real data-plane client."""
    print_section("4. Memory — Context Continuity")
    print(f"  [Memory]  Loading context for actorId={ACTOR_ID}, sessionId={SESSION_ID}")
    print("  [Memory]  Short-term: active dialogue within this session")
    print("  [Memory]  Long-term: facts/preferences persisted across sessions")
    print("  [Memory]  Strategies: semantic, summarization, user preference, episodic, custom")
    print("  NOTE: Memory is a data store — tenant partitioning and PII redaction are your responsibility")


def step_5_observability():
    """Observability emits OpenTelemetry-compatible traces to CloudWatch.
    latency and tool_calls below are computed from STEP_TIMINGS and
    TOOL_CALLS — the measurements taken while steps 1-4 actually ran."""
    print_section("5. Observability — End-to-End Trace")
    total_latency = sum(STEP_TIMINGS.values())
    trace = {
        "traceId": "0af7651916cd43dd8448eb211c80319c",
        "rootSpan": f"agent.run ({total_latency * 1000:.1f}ms measured across steps 1-4)",
        "childSpans": [
            f"{name} — {duration * 1000:.2f}ms (measured)"
            for name, duration in STEP_TIMINGS.items()
        ],
        "signals": {
            "latency_ms": round(total_latency * 1000, 2),
            "tool_calls": len(TOOL_CALLS),
            "tool_call_detail": TOOL_CALLS,
            "errors": sum(1 for call in TOOL_CALLS if call["status"] != "Success"),
        },
    }
    print(f"  [Observability] {json.dumps(trace, indent=2)}")
    print("  [CloudWatch] A live request's trace appears in the Generative AI Observability dashboard")
    print("  NOTE: Traces contain prompts/tool args — redact sensitive data at write time")


def main():
    print("AgentCore Request Lifecycle — Instructor Walkthrough")
    print(f"Runtime: {AGENT_RUNTIME_ARN}\n")

    caller = timed_step("identity", step_1_identity)
    timed_step("runtime", step_2_runtime, caller)
    timed_step("gateway", step_3_gateway)
    timed_step("memory", step_4_memory)
    step_5_observability()

    print_section("Takeaway")
    print("  Each capability governs a specific boundary in the request lifecycle.")
    print("  Runtime isolates compute. Gateway governs tools. Identity separates")
    print("  callers from workloads. Memory provides state. Observability gives")
    print("  visibility. Together they form the production-ready agent platform.")


if __name__ == "__main__":
    main()
