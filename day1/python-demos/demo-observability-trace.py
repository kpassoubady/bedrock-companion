"""
Demo — AgentCore Observability Trace Inspection
Day 1 — Block 4: State and Visibility (Memory and Observability)

Inspects a synthetic OpenTelemetry-style fixture representing an agent
execution. analyze_trace() reads its numbers straight out of the trace's
own spans — total duration from the root span's start/end timestamps,
token totals from a sum() over the gen_ai spans, tool/memory/error counts
from list comprehensions — so deleting or editing a span changes what
gets printed.

No AWS credentials or API calls required.
Run: python3 day1/demos/demo-observability-trace.py
"""
import json
from datetime import datetime, timedelta, timezone

# Rough per-token pricing used only to illustrate cost attribution.
PRICE_PER_INPUT_TOKEN = 0.000003
PRICE_PER_OUTPUT_TOKEN = 0.000015


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def build_trace() -> dict:
    """Build the OpenTelemetry-compatible fixture that analyze_trace()
    will read. The traceId and span structure follow OTel conventions."""
    base_time = datetime(2026, 8, 2, 10, 0, 0, tzinfo=timezone.utc)

    return {
        "traceId": "0af7651916cd43dd8448eb211c80319c",
        "resource": {
            "service.name": "AgentCore",
            "agent.id": "TravelAgent-Prod",
        },
        "spans": [
            {
                "spanId": "ROOT-1",
                "parentSpanId": None,
                "name": "agent.run",
                "kind": "SERVER",
                "startTime": base_time.isoformat(),
                "endTime": (base_time + timedelta(seconds=4.5)).isoformat(),
                "attributes": {
                    "agent.session_id": "sess-888",
                    "agent.principal": "user-123",
                    "agent.status": "success",
                },
            },
            {
                "spanId": "CHILD-1",
                "parentSpanId": "ROOT-1",
                "name": "gen_ai.client.operation",
                "kind": "CLIENT",
                "startTime": (base_time + timedelta(milliseconds=100)).isoformat(),
                "endTime": (base_time + timedelta(seconds=2)).isoformat(),
                "attributes": {
                    "gen_ai.operation.name": "chat",
                    "gen_ai.request.model": "anthropic.claude-3-sonnet-20240229-v1:0",
                    "gen_ai.usage.input_tokens": 450,
                    "gen_ai.usage.output_tokens": 65,
                    "gen_ai.response.finish_reasons": ["tool_calls"],
                },
            },
            {
                "spanId": "CHILD-2",
                "parentSpanId": "ROOT-1",
                "name": "agent.tool_call",
                "kind": "CLIENT",
                "startTime": (base_time + timedelta(seconds=2, milliseconds=100)).isoformat(),
                "endTime": (base_time + timedelta(seconds=2, milliseconds=500)).isoformat(),
                "attributes": {
                    "tool.name": "check_weather",
                    "tool.status": "Success",
                    "tool.duration_ms": 400,
                },
            },
            {
                "spanId": "CHILD-3",
                "parentSpanId": "ROOT-1",
                "name": "agent.memory_operation",
                "kind": "CLIENT",
                "startTime": (base_time + timedelta(seconds=2, milliseconds=100)).isoformat(),
                "endTime": (base_time + timedelta(seconds=2, milliseconds=150)).isoformat(),
                "attributes": {
                    "memory.operation": "read",
                    "memory.namespace": "/summary/user-123/sess-888/",
                    "memory.results_count": 3,
                },
            },
            {
                "spanId": "CHILD-4",
                "parentSpanId": "ROOT-1",
                "name": "gen_ai.client.operation",
                "kind": "CLIENT",
                "startTime": (base_time + timedelta(seconds=2, milliseconds=600)).isoformat(),
                "endTime": (base_time + timedelta(seconds=4, milliseconds=400)).isoformat(),
                "attributes": {
                    "gen_ai.operation.name": "chat",
                    "gen_ai.request.model": "anthropic.claude-3-sonnet-20240229-v1:0",
                    "gen_ai.usage.input_tokens": 580,
                    "gen_ai.usage.output_tokens": 120,
                    "gen_ai.response.finish_reasons": ["stop"],
                },
            },
        ],
    }


def show_trace_structure(trace: dict):
    """Show the complete trace with all spans."""
    print_section("End-to-End Trace — Full Span Hierarchy")
    print(f"  {json.dumps(trace, indent=2)}")


def analyze_trace(trace: dict) -> dict:
    """Compute every signal from the trace's own spans.

    Stage-level telemetry is more useful than a single request-duration
    metric — this function proves it by deriving each stage's contribution
    directly from the spans, not from a second, disconnected literal."""
    print_section("Key Trace Signals — Computed From the Spans Above")

    spans = trace["spans"]
    root = next(s for s in spans if s["parentSpanId"] is None)
    llm_spans = [s for s in spans if s["name"] == "gen_ai.client.operation"]
    tool_spans = [s for s in spans if s["name"] == "agent.tool_call"]
    memory_spans = [s for s in spans if s["name"] == "agent.memory_operation"]

    total_duration = (
        datetime.fromisoformat(root["endTime"]) - datetime.fromisoformat(root["startTime"])
    ).total_seconds()
    input_tokens = sum(s["attributes"].get("gen_ai.usage.input_tokens", 0) for s in llm_spans)
    output_tokens = sum(s["attributes"].get("gen_ai.usage.output_tokens", 0) for s in llm_spans)
    tool_errors = sum(1 for s in tool_spans if s["attributes"].get("tool.status") != "Success")
    estimated_cost = input_tokens * PRICE_PER_INPUT_TOKEN + output_tokens * PRICE_PER_OUTPUT_TOKEN

    signals = {
        "total_duration_s": round(total_duration, 3),
        "llm_calls": len(llm_spans),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": len(tool_spans),
        "tool_errors": tool_errors,
        "memory_operations": len(memory_spans),
        "estimated_cost_usd": round(estimated_cost, 6),
    }

    print(f"  {json.dumps(signals, indent=2)}")
    print()
    for span in llm_spans + tool_spans + memory_spans:
        duration_ms = (
            datetime.fromisoformat(span["endTime"]) - datetime.fromisoformat(span["startTime"])
        ).total_seconds() * 1000
        print(f"  {duration_ms:>7.1f} ms  {span['name']:<28} spanId={span['spanId']}")
    print()
    print("  Why stage-level telemetry matters:")
    print(f"  - Single request-duration metric ({total_duration:.1f}s) tells you it was slow")
    print("  - The per-span breakdown above tells you which LLM call and which tool call cost what")
    print("  - You can optimize the right phase, not guess")
    return signals


def show_cloudwatch_integration():
    """Explain how this fixture's shape maps to CloudWatch's real dashboards.

    This is a synthetic fixture, not a CloudWatch export — the live lab
    is where students view a real trace in the console."""
    print_section("CloudWatch Generative AI Observability")

    print("  This fixture is shaped like the spans CloudWatch Generative AI")
    print("  Observability renders for a real AgentCore invocation. CloudWatch provides:")
    print("  - Agent View: agent count, sessions, traces, error rate, throttle rate")
    print("  - Trace View: end-to-end span waterfall with timing")
    print("  - Model View: token usage, latency, cost per model")
    print("  - Tool View: tool invocation count, errors, latency per tool")
    print()
    print("  Console path: CloudWatch → Generative AI Observability → AgentCore tab")
    print()
    print("  What students do in the lab:")
    print("  - Deploy agent, invoke it, then navigate to CloudWatch")
    print("  - Find their trace by session ID or time range")
    print("  - Identify: total latency, token use, tool calls, errors")


def show_trace_governance():
    """Explain trace redaction, retention, and access control.

    Trace payloads can contain prompts, tool arguments, and model
    responses — they require the same data governance as application logs."""
    print_section("Trace Governance — Data Protection")

    print("  Trace payloads may contain:")
    print("  - User prompts (potentially containing PII)")
    print("  - Tool arguments (potentially containing credentials or PII)")
    print("  - Model responses (potentially containing generated PII)")
    print()
    print("  Required governance controls:")
    print("  1. Redact PII at write time (before trace hits CloudWatch)")
    print("  2. Set CloudWatch log group retention policy (e.g., 30 days)")
    print("  3. Restrict CloudWatch access with IAM (least privilege)")
    print("  4. Encrypt trace data at rest (CloudWatch default + KMS CMK)")
    print("  5. Audit who accessed which traces (CloudTrail + CloudWatch Logs)")
    print()
    print("  Traces are forensic evidence — without them, incident analysis is guesswork.")


def main():
    print("AgentCore Observability Trace — Instructor Demo\n")

    trace = build_trace()
    show_trace_structure(trace)
    analyze_trace(trace)
    show_cloudwatch_integration()
    show_trace_governance()

    print_section("Key Takeaways")
    print("  1. Stage-level telemetry is more useful than a single duration metric")
    print("  2. Key signals: latency, token use, tool activity, memory ops, errors, cost")
    print("  3. Every signal above is computed from the trace's own spans")
    print("  4. Trace payloads may contain sensitive data — redact at write time")
    print("  5. Observability supports detection, response, evaluation, and audit")


if __name__ == "__main__":
    main()
