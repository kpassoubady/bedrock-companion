"""
Demo — Three-Identity Separation
Day 1 — Block 3: Securing the Agent (Identity and Least Privilege)

Demonstrates the three distinct identities in an AgentCore request flow:
1. Caller Identity (human user)
2. Workload Identity (Runtime execution role)
3. Downstream Credential (tool access token)

The downstream credential's expiry is computed from the current time (not
a hardcoded past timestamp), and the OWASP ASI03 blast-radius comparison is
computed from two small permission maps rather than narrated in prose.

Offline identity-flow walkthrough. No AWS credentials or API calls required.
Run: python3 day1/demos/demo-identity-separation.py
"""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

# --- Configuration ---
CALLER_ID = os.environ.get("CALLER_ID", "user-finance-881")
WORKLOAD_ROLE_ARN = os.environ.get(
    "WORKLOAD_ROLE_ARN",
    "arn:aws:iam::123456789012:role/ProdAgentRole",
)

# Per-agent action sets used to compute blast radius under each pattern.
AGENT_ACTIONS = {
    "BillingAgent": {"bedrock:InvokeModel", "billing:CreateInvoice"},
    "SupportAgent": {"bedrock:InvokeModel", "support:ReadTicket"},
    "RefundAgent": {"bedrock:InvokeModel", "finance:RequestApproval"},
}


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def step_1_caller_identity():
    """The human caller authenticates at the public edge (API Gateway / BFF).
    Their identity is verified but NOT passed as credentials to the agent."""
    print_section("1. Caller Identity — Who Initiated the Request?")

    print("  [API Gateway] Authenticating caller via Amazon Cognito")
    print(f"  [API Gateway] Caller JWT verified: user_id={CALLER_ID}, role=FinanceViewer")
    print("  [API Gateway] Caller context propagated, credentials NOT shared with agent")
    print()
    print("  Key principle: The agent does NOT run as the human user.")
    print("  The caller's credentials are never exposed to agent code.")

    return {"user_id": CALLER_ID, "role": "FinanceViewer"}


def step_2_workload_identity(caller: dict):
    """The Runtime execution role is the agent's operational identity.
    It governs infrastructure actions (invoke Gateway, emit logs, etc.).

    This is where least privilege matters: never use bedrock:* in production."""
    print_section("2. Workload Identity — What Can the Agent Do?")

    print(f"  [Runtime] Agent session started for caller: {caller['user_id']}")
    print(f"  [Runtime] Workload role: {WORKLOAD_ROLE_ARN}")
    print()
    print("  This role grants ONLY:")
    print("  - bedrock-agentcore:InvokeGateway (on one specific Gateway)")
    print("  - logs:PutLogEvents (on specific log group)")
    print("  - bedrock:InvokeModel (on specific model ARN)")
    print()
    print("  This role does NOT grant:")
    print("  - bedrock:* (never in production)")
    print("  - s3:* (agent doesn't need S3)")
    print("  - dynamodb:* (agent doesn't need DynamoDB)")
    print()
    print("  The attribution gap: without a distinct workload identity,")
    print("  CloudTrail shows 'the role did it' — not which agent or caller.")


def step_3_downstream_credential():
    """When the agent invokes a tool through Gateway, it uses a scoped,
    short-lived downstream credential — not the caller's credentials.

    exp is computed from the current time, so the token is always
    genuinely short-lived relative to whenever this demo actually runs."""
    print_section("3. Downstream Credential — What Data Can the Agent Access?")

    print("  [Identity Directory] Issuing scoped access token for tool invocation")
    issued_at = datetime.now(timezone.utc)
    ttl = timedelta(minutes=15)
    expires_at = issued_at + ttl
    token_claims = {
        "sub": f"agent-session-{str(uuid.uuid4())[:8]}",  # display label only; iat/exp below are the load-bearing fields
        "on_behalf_of": CALLER_ID,
        "scope": "invoice:read",
        "iat": issued_at.isoformat(),
        "exp": expires_at.isoformat(),
        "tool": "Finance-Invoice-API",
    }
    print(f"  Token claims:\n  {json.dumps(token_claims, indent=2)}")
    print()
    print(f"  Computed lifetime: {ttl.total_seconds() / 60:.0f} minutes "
          f"(issued {issued_at.isoformat()}, expires {expires_at.isoformat()})")
    print()
    print("  Key properties of the downstream credential:")
    print("  - Short-lived (expires in minutes, not days)")
    print("  - Task-scoped (invoice:read only, not invoice:write)")
    print("  - On-behalf-of claim preserves caller attribution")
    print("  - Never exposes the caller's own credentials")


def compute_blast_radius(compromised_agent: str, shared_credential: bool) -> set:
    """Compute which actions a hijacked agent can reach.

    Under a shared credential, every agent uses the same role, so
    compromising any one of them reaches the union of all agents'
    permissions. Under dedicated identities, it reaches only its own."""
    if shared_credential:
        return set().union(*AGENT_ACTIONS.values())
    return set(AGENT_ACTIONS[compromised_agent])


def show_identity_aggregation_risk():
    """OWASP ASI03: agents are identity aggregation points.
    Compromise one agent, inherit all its permissions.

    The comparison below is computed from AGENT_ACTIONS — editing any
    agent's action set changes the printed reach and reduction numbers."""
    print_section("OWASP ASI03 — Identity Aggregation Risk")

    print("  Every AI agent operates with the combined authority of every")
    print("  token, key, and credential assigned to it.")
    print()

    compromised = "RefundAgent"
    shared_reach = compute_blast_radius(compromised, shared_credential=True)
    dedicated_reach = compute_blast_radius(compromised, shared_credential=False)

    print(f"  Scenario: {compromised} is hijacked via prompt injection.")
    print()
    print(f"  Level 1 (Initial) — one shared key across {len(AGENT_ACTIONS)} agents:")
    print(f"    Reachable actions ({len(shared_reach)}): {sorted(shared_reach)}")
    print(f"    Also exposes {sorted(a for a in AGENT_ACTIONS if a != compromised)} — they share the same credential.")
    print()
    print(f"  Level 2 (Emerging) — dedicated identity per agent:")
    print(f"    Reachable actions ({len(dedicated_reach)}): {sorted(dedicated_reach)}")
    print(f"    Other agents are unaffected: their credentials were never shared.")
    print()
    reduction = len(shared_reach) - len(dedicated_reach)
    print(f"  Computed blast-radius reduction: {reduction} fewer reachable action(s), "
          f"and {len(AGENT_ACTIONS) - 1} agent(s) stay unaffected instead of {len(AGENT_ACTIONS) - 1} being co-compromised.")
    print()
    print("  The three-identity separation is not optional for production.")


def main():
    print("Three-Identity Separation — Instructor Demo\n")

    caller = step_1_caller_identity()
    step_2_workload_identity(caller)
    step_3_downstream_credential()
    show_identity_aggregation_risk()

    print_section("Key Takeaways")
    print("  1. A production request traverses three distinct identities")
    print("  2. The agent is a governed principal — it does NOT run as the user")
    print("  3. Least-privilege IAM is a deterministic control, not a prompt")
    print("  4. Agents are identity aggregation points — scope every credential")
    print("  5. CloudTrail audit trail maps action → workload → caller")


if __name__ == "__main__":
    main()
