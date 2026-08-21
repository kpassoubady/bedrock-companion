"""
Demo — Least Privilege IAM Policy Comparison
Day 1 — Block 3: Securing the Agent (Identity and Least Privilege)

Computes a real set-difference between a broad development policy and a
restricted production policy — the printed conclusion is derived from the
policy dicts, so editing either policy changes what gets printed. Students
learn to move from Level 1 (Initial: bedrock:*) to Level 2 (Emerging:
scoped, per-resource permissions).

Run: python3 day1/demos/demo-least-privilege-iam.py
"""
import json


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def extract_actions_and_resources(policy: dict) -> tuple[set, set]:
    """Read the actual Action and Resource fields out of every statement."""
    actions, resources = set(), set()
    for statement in policy["Statement"]:
        stmt_actions = statement["Action"]
        stmt_resources = statement["Resource"]
        actions.update(stmt_actions if isinstance(stmt_actions, list) else [stmt_actions])
        resources.update(stmt_resources if isinstance(stmt_resources, list) else [stmt_resources])
    return actions, resources


def compare_policies(broad: dict, restricted: dict) -> dict:
    """Compute the comparison instead of narrating a fixed conclusion."""
    broad_actions, broad_resources = extract_actions_and_resources(broad)
    restricted_actions, restricted_resources = extract_actions_and_resources(restricted)

    broad_is_wildcard_action = "bedrock:*" in broad_actions or "*" in broad_actions
    broad_is_wildcard_resource = "*" in broad_resources

    return {
        "broad_action_count": len(broad_actions),
        "broad_resource_count": len(broad_resources),
        "broad_is_wildcard_action": broad_is_wildcard_action,
        "broad_is_wildcard_resource": broad_is_wildcard_resource,
        "restricted_action_count": len(restricted_actions),
        "restricted_resource_count": len(restricted_resources),
        "restricted_actions": sorted(restricted_actions),
        "restricted_resources": sorted(restricted_resources),
    }


def show_broad_policy() -> dict:
    """Level 1 (Initial): Broad development policy — NOT for production."""
    print_section("Level 1: Broad Development Policy (NOT for Production)")

    broad_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["bedrock:*"],
                "Resource": "*",
            }
        ],
    }

    print("  This policy allows the agent to invoke ANY Bedrock model")
    print("  and access ANY Bedrock resource in the account.")
    print()
    print(f"  {json.dumps(broad_policy, indent=2)}")
    return broad_policy


def show_restricted_policy() -> dict:
    """Level 2 (Emerging): Restricted production policy — least privilege."""
    print_section("Level 2: Restricted Production Policy (Least Privilege)")

    restricted_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSpecificModelInference",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
            },
            {
                "Sid": "AllowGatewayInvocation",
                "Effect": "Allow",
                "Action": ["bedrock-agentcore:InvokeGateway"],
                "Resource": "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/ProdGateway",
            },
            {
                "Sid": "AllowLogging",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/bedrock/agentcore/*",
            },
        ],
    }

    print(f"  {json.dumps(restricted_policy, indent=2)}")
    return restricted_policy


def show_comparison(broad_policy: dict, restricted_policy: dict):
    """Print a conclusion computed from the two policy dicts above."""
    print_section("Computed Comparison — Level 1 vs. Level 2")

    result = compare_policies(broad_policy, restricted_policy)

    print(f"  Level 1 grants {result['broad_action_count']} action pattern(s) "
          f"on {result['broad_resource_count']} resource pattern(s).")
    print(f"  Level 1 resource scope is wildcard: {result['broad_is_wildcard_resource']}")
    print()
    print(f"  Level 2 grants exactly {result['restricted_action_count']} named actions "
          f"across {result['restricted_resource_count']} scoped resources:")
    for action in result["restricted_actions"]:
        print(f"    - {action}")
    print()
    if result["broad_is_wildcard_action"] and result["broad_is_wildcard_resource"]:
        print(f"  Verdict: every one of Level 2's {result['restricted_action_count']} named actions "
              "is already covered by Level 1's bedrock:* on Resource: *.")
        print("  Level 1 grants everything Level 2 grants, plus every other Bedrock action and resource in the account.")
    else:
        print("  Verdict: Level 1 no longer contains an unconditional wildcard — recompute before trusting this comparison.")


def show_permission_boundaries():
    """Demonstrate IAM permission boundaries as a structural control.

    Permission boundaries set the maximum permissions any identity
    in an account can have — a guardrail above IAM policies."""
    print_section("IAM Permission Boundaries — Structural Control")

    boundary = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AgentCoreOnly",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock-agentcore:InvokeAgentRuntime",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": "*",
            }
        ],
    }

    print("  Permission boundaries set the MAXIMUM permissions any role")
    print("  in the account can have — even if an admin attaches a broader policy.")
    print()
    print(f"  {json.dumps(boundary, indent=2)}")
    print()
    print("  Key insight from AWS security principle #3:")
    print("  'Deterministic external controls are the starting point for agentic security.'")
    print("  IAM policies, permission boundaries, and scoped tokens are deterministic.")
    print("  Prompt instructions ('do not access PII') are not.")


def main():
    print("Least Privilege IAM — Policy Comparison\n")

    broad_policy = show_broad_policy()
    restricted_policy = show_restricted_policy()
    show_comparison(broad_policy, restricted_policy)
    show_permission_boundaries()

    print_section("Key Takeaways")
    print("  1. Never use bedrock:* in production — it violates least privilege")
    print("  2. Scope every policy to specific resources (model ARN, Gateway ARN)")
    print("  3. IAM is a deterministic control — it's mathematically enforceable")
    print("  4. Permission boundaries provide a structural guardrail above IAM policies")
    print("  5. Prompt-level instructions are not security controls")


if __name__ == "__main__":
    main()
