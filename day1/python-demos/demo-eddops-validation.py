"""
Demo — EDDOps Golden Dataset Validation
Day 1 — Block 6: Best Practices and Wrap-Up

Demonstrates Evaluation-Driven Development (EDDOps): gating agent
promotion using a golden dataset. The evaluation pipeline is kept separate
from AWS Agent Registry record states. The narrated gate threshold below
matches the coded threshold exactly (100% exact-match, i.e. score == 1) —
with only 3 test cases, anything short of 100% is unreachable as "≥95%".

Run: python3 day1/demos/demo-eddops-validation.py
"""
import json


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def show_eddops_pipeline():
    """Explain the EDDOps promotion pipeline.

    This application delivery pipeline is gated by evaluation evidence. AWS
    Agent Registry record approval has separate DRAFT, PENDING_APPROVAL, and
    APPROVED states."""
    print_section("EDDOps — Evaluation-Driven Development Pipeline")

    pipeline = {
        "stages": [
            {
                "stage": "DRAFT",
                "description": "Agent under active development",
                "gate": "Code review + unit tests",
            },
            {
                "stage": "REVIEW",
                "description": "Agent awaiting evaluation",
                "gate": "Golden dataset evaluation (100% exact-match pass rate — any regression blocks promotion)",
            },
            {
                "stage": "PUBLISHED",
                "description": "Agent serving production traffic",
                "gate": "Canary deployment + monitoring period",
            },
        ],
        "rollback": "Alias update to previous PUBLISHED version",
    }

    print(f"  {json.dumps(pipeline, indent=2)}")
    print()
    print("  This is the APPLICATION delivery pipeline: DRAFT -> REVIEW -> PUBLISHED.")
    print("  AWS Agent Registry has its own, separate approval states: DRAFT -> PENDING_APPROVAL -> APPROVED.")
    print("  A record can be Registry-APPROVED while its application pipeline is still in REVIEW, and vice versa.")
    print()
    print("  Key principle: Agent promotion is gated by evidence, not trust.")
    print("  A code change that passes review but fails evaluation does NOT ship.")


def run_golden_dataset_evaluation(agent_version: str):
    """Evaluate recorded agent outputs against tool and parameter assertions."""
    print_section(f"Golden Dataset Evaluation — {agent_version}")

    golden_dataset = [
        {
            "input": "Show Salesforce case 00001042",
            "expected": {"tool": "get_case", "params": {"case_number": "00001042"}},
        },
        {
            "input": "Refund order ORD-1001",
            "expected": {"tool": "request_approval", "params": {"order_id": "ORD-1001"}},
        },
        {
            "input": "What is the status of order ORD-1001?",
            "expected": {"tool": "get_order_status", "params": {"order_id": "ORD-1001"}},
        },
    ]
    recorded_outputs = {
        "v1.0-draft": [item["expected"] for item in golden_dataset],
        "v2.0-draft": [
            golden_dataset[0]["expected"],
            {"tool": "issue_refund", "params": {"order_id": "ORD-1001"}},
            golden_dataset[2]["expected"],
        ],
    }

    results = []
    for item, actual in zip(golden_dataset, recorded_outputs[agent_version]):
        passed = actual == item["expected"]
        results.append({"input": item["input"], "expected": item["expected"], "actual": actual, "passed": passed})
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] Input: '{item['input']}'")
        print(f"         Expected: {item['expected']}")
        print(f"         Actual:   {actual}")

    score = sum(result["passed"] for result in results) / len(results)
    print(f"\n  Evaluation Score: {score * 100:.0f}% ({sum(r['passed'] for r in results)}/{len(results)} exact matches, gate requires 100%)")
    print("  Status: APPROVED" if score == 1 else "  Status: REJECTED, Fix regression and re-evaluate")
    return results


def show_production_best_practices():
    """Five production best practices for agent operations."""
    print_section("Five Production Best Practices")

    practices = [
        {
            "practice": "1. Continuous Evaluation (EDDOps)",
            "description": "Gate promotion on golden-dataset evidence, not code review alone",
            "implementation": "CI/CD stage runs evals → pass/fail gates promotion",
        },
        {
            "practice": "2. Deterministic Boundaries",
            "description": "Use IAM, tool allowlists, and network rules — not prompts — for security",
            "implementation": "IAM policies, Gateway allowlists, VPC egress rules",
        },
        {
            "practice": "3. Multi-Agent Validation",
            "description": "Validator agent reviews primary agent's output before execution",
            "implementation": "Step Functions orchestrate primary → validator → execute or escalate",
        },
        {
            "practice": "4. Human-in-the-Loop (HITL)",
            "description": "Human escalation is a designed workflow component, not a failure mode",
            "implementation": "Defined SLAs, approval UI, audit trail for human decisions",
        },
        {
            "practice": "5. Observability is Non-Negotiable",
            "description": "End-to-end tracing is mandatory for root-cause analysis",
            "implementation": "CloudWatch dashboards, alarms, anomaly detection, cost attribution",
        },
    ]

    for p in practices:
        print(f"\n  {p['practice']}")
        print(f"    {p['description']}")
        print(f"    → {p['implementation']}")


def main():
    print("EDDOps and Production Best Practices — Instructor Demo\n")

    show_eddops_pipeline()

    print("\n" + "=" * 60)
    print("  Scenario 1: Stable version (v1.0)")
    print("=" * 60)
    run_golden_dataset_evaluation("v1.0-draft")

    print("\n" + "=" * 60)
    print("  Scenario 2: Regression detected (v2.0)")
    print("=" * 60)
    run_golden_dataset_evaluation("v2.0-draft")

    show_production_best_practices()

    print_section("Key Takeaways")
    print("  1. EDDOps gates promotion on evaluation evidence, not trust")
    print("  2. Golden datasets define correct behavior — deviation = regression")
    print("  3. Registry approval states are separate from application deployment stages")
    print("  4. Five production practices span eval, security, validation, HITL, observability")
    print("  5. AgentCore provides infrastructure; you provide governance and business logic")


if __name__ == "__main__":
    main()
