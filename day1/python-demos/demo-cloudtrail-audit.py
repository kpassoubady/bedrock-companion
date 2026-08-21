"""
Demo — CloudTrail Audit Evidence
Day 1 — Block 3: Securing the Agent (Identity and Least Privilege)

Analyzes two synthetic, redacted CloudTrail-style fixtures — the backend's
InvokeAgentRuntime call and the Runtime workload's own downstream
InvokeGateway call — and correlates them by runtimeSessionId. A single
CloudTrail event only shows who called Runtime; it takes a second,
correlated event to see what identity the code ran as once inside.

Run: python3 day1/demos/demo-cloudtrail-audit.py
"""
import json


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def build_cloudtrail_events() -> tuple[dict, dict]:
    """Two correlated, synthetic CloudTrail-style events for one request."""
    runtime_session_id = "session-99x-isolated-000000000000001"

    invoke_event = {
        "eventVersion": "1.08",
        "eventTime": "2026-08-02T14:40:00Z",
        "eventSource": "bedrock-agentcore.amazonaws.com",
        "eventName": "InvokeAgentRuntime",
        "awsRegion": "us-east-1",
        "userIdentity": {
            "type": "AssumedRole",
            "arn": "arn:aws:sts::111122223333:assumed-role/ApprovedAgentBackend/req-7f3a9c",
        },
        "requestParameters": {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:111122223333:runtime/SalesforceCaseDemo-abcdefghij",
            "runtimeSessionId": runtime_session_id,
            "runtimeUserId": "salesforce-user-881",
        },
        "responseElements": {"statusCode": 200},
    }

    downstream_event = {
        "eventVersion": "1.08",
        "eventTime": "2026-08-02T14:40:01Z",
        "eventSource": "bedrock-agentcore.amazonaws.com",
        "eventName": "InvokeGateway",
        "awsRegion": "us-east-1",
        "userIdentity": {
            "type": "AssumedRole",
            "arn": "arn:aws:sts::111122223333:assumed-role/ProdAgentRole/session-99x-isolated",
        },
        "requestParameters": {
            "gatewayArn": "arn:aws:bedrock-agentcore:us-east-1:111122223333:gateway/ProdGateway",
            "runtimeSessionId": runtime_session_id,
        },
        "responseElements": {"statusCode": 200},
    }

    return invoke_event, downstream_event


def show_cloudtrail_events(invoke_event: dict, downstream_event: dict):
    """Print both events exactly as audit_breakdown() will read them."""
    print_section("CloudTrail Event 1 — InvokeAgentRuntime (backend caller)")
    print(f"  {json.dumps(invoke_event, indent=2)}")

    print_section("CloudTrail Event 2 — InvokeGateway (Runtime workload)")
    print(f"  {json.dumps(downstream_event, indent=2)}")


def audit_breakdown(invoke_event: dict, downstream_event: dict):
    """Index both event dicts to answer each attribution question — nothing
    printed here is a value that doesn't appear in the fixtures above."""
    print_section("Audit Breakdown — Who Did What?")

    same_session = (
        invoke_event["requestParameters"]["runtimeSessionId"]
        == downstream_event["requestParameters"]["runtimeSessionId"]
    )

    print("  1. Which backend invoked Runtime? (API caller identity)")
    print(f"     → {invoke_event['userIdentity']['arn']}")
    print()
    print("  2. What identity did the code run as inside Runtime? (Workload identity)")
    print(f"     → {downstream_event['userIdentity']['arn']}")
    print("     (Not visible in event 1 — this only appears once the workload makes its own call.)")
    print()
    print("  3. Which agent was invoked? (Resource)")
    print(f"     → {invoke_event['requestParameters']['agentRuntimeArn']}")
    print()
    print("  4. Are these two events part of the same Runtime session?")
    print(f"     → {'Yes' if same_session else 'No'} "
          f"(runtimeSessionId {'matches' if same_session else 'does not match'}: "
          f"{invoke_event['requestParameters']['runtimeSessionId']!r} vs. "
          f"{downstream_event['requestParameters']['runtimeSessionId']!r})")
    print()
    print("  5. When did the request start? (Timestamp)")
    print(f"     → {invoke_event['eventTime']}")
    print()
    print("  Without correlating both events by runtimeSessionId:")
    print("  - Event 1 alone shows only the backend caller, not the workload identity")
    print("  - Impossible to prove which workload role actually executed the agent's code")
    print("  - Security incident response cannot trace blast radius per user")


def show_audit_best_practices():
    """Best practices for agent audit trails."""
    print_section("Audit Best Practices for Agentic Systems")

    practices = [
        "Enable CloudTrail across all regions where AgentCore resources exist",
        "Correlate events by runtimeSessionId to reconstruct caller → workload → tool",
        "Correlate the verified caller in application telemetry using a non-sensitive request ID",
        "Use distinct workload identities per agent (not one shared role)",
        "Tag all AgentCore resources with owner, environment, and cost center",
        "Set CloudWatch alarms on anomalous invocation patterns (spike in errors, new agents)",
        "Retain CloudTrail logs per compliance requirements (typically 90 days minimum)",
        "Forward AgentCore CloudTrail events to your SIEM for correlation",
    ]

    for i, practice in enumerate(practices, 1):
        print(f"  {i}. {practice}")


def main():
    print("CloudTrail Audit Evidence — Instructor Demo\n")

    invoke_event, downstream_event = build_cloudtrail_events()
    show_cloudtrail_events(invoke_event, downstream_event)
    audit_breakdown(invoke_event, downstream_event)
    show_audit_best_practices()

    print_section("Key Takeaways")
    print("  1. One CloudTrail event shows the backend caller — not the workload identity")
    print("  2. Correlating events by runtimeSessionId reveals what ran inside Runtime")
    print("  3. Runtime workload and downstream credentials need separate evidence")
    print("  4. Forward AgentCore events to your SIEM for enterprise visibility")


if __name__ == "__main__":
    main()
