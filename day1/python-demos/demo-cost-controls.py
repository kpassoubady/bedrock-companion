"""
Demo — Cost Controls and Runaway Execution Prevention
Day 1 — Block 6: Best Practices and Wrap-Up

Computes a real per-request cost estimate across Runtime/LLM/Gateway/Memory
dimensions for two different request shapes, so the printed "amplification"
claim is a division of two computed totals rather than a prose assertion.
Lifecycle numbers live in demo-runtime-deploy.py; this demo does not
restate them.

Run: python3 day1/demos/demo-cost-controls.py
"""
import json

# Rough unit prices used only to illustrate cost attribution across services.
PRICE_PER_1K_INPUT_TOKENS = 0.003
PRICE_PER_1K_OUTPUT_TOKENS = 0.015
PRICE_PER_GATEWAY_CALL = 0.0001
PRICE_PER_MEMORY_OP = 0.00002


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def estimate_request_cost(input_tokens: int, output_tokens: int, tool_calls: int, memory_ops: int) -> dict:
    """Compute a per-request cost from real per-service unit prices."""
    llm_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
    gateway_cost = tool_calls * PRICE_PER_GATEWAY_CALL
    memory_cost = memory_ops * PRICE_PER_MEMORY_OP
    return {
        "llm": llm_cost,
        "gateway": gateway_cost,
        "memory": memory_cost,
        "total": llm_cost + gateway_cost + memory_cost,
    }


def show_cost_dimensions():
    """AgentCore costs span multiple billing dimensions — compute two
    request shapes to show how those dimensions actually stack."""
    print_section("Emergent Cost Dimensions — Computed, Not Narrated")

    light = estimate_request_cost(input_tokens=450, output_tokens=65, tool_calls=1, memory_ops=1)
    heavy = estimate_request_cost(input_tokens=1030, output_tokens=185, tool_calls=3, memory_ops=4)

    print("  Light single-turn request (1 LLM call, 1 tool call, 1 memory op):")
    print(f"    {json.dumps({k: round(v, 6) for k, v in light.items()}, indent=4)}")
    print()
    print("  Heavy multi-tool request (2 LLM calls, 3 tool calls, 4 memory ops):")
    print(f"    {json.dumps({k: round(v, 6) for k, v in heavy.items()}, indent=4)}")
    print()
    amplification = heavy["total"] / light["total"]
    print(f"  Computed cost amplification factor: {amplification:.2f}x")
    print("  → Rate limiting and budgets must account for this amplification factor,")
    print("    not just the number of user-visible requests.")


def show_idle_timeout():
    """Idle timeout and max lifetime prevent idle instance billing.

    The exact idleRuntimeSessionTimeout/maxLifetime values are set in
    demo-runtime-deploy.py's lifecycleConfiguration — this section is
    about the application-side habit of not waiting for those caps."""
    print_section("Proactive Termination — Don't Wait for the Timeout")

    print("  demo-runtime-deploy.py's lifecycleConfiguration already sets")
    print("  idleRuntimeSessionTimeout and maxLifetime as Runtime-side caps.")
    print()
    print("  Those caps are a backstop, not a plan:")
    print("  - A session idle for 4m59s still bills for the full window before the cap fires")
    print("  - maxLifetime replaces compute after 8 hours; it doesn't know the task finished at minute 3")
    print()
    print("  Best practice: call StopRuntimeSession the moment your application logic")
    print("  detects the task is done — don't rely on the Runtime cap to notice for you.")


def show_runaway_execution():
    """Demonstrate hallucination loops and deterministic limits."""
    print_section("Runaway Execution — Hallucination Loops")

    print("  A hallucination loop occurs when an agent:")
    print("  1. Calls a tool → tool returns error")
    print("  2. Agent retries with slightly different parameters → same error")
    print("  3. Agent retries again → same error")
    print("  4. Repeats indefinitely, consuming tokens and API calls")
    print()
    print("  Deterministic controls to prevent this:")
    controls = {
        "max_iterations": "Hard cap on reasoning steps per request (e.g., 50)",
        "harness_timeout": "Wall-clock timeout per request (e.g., 600s)",
        "circuit_breaker": "Halt if N consecutive tool calls fail",
        "spend_budget": "Max cost per request (tokens × model price)",
        "idempotency_keys": "Prevent duplicate side effects on retry",
    }
    print(f"  {json.dumps(controls, indent=2)}")
    print()
    print("  CRITICAL: Do NOT rely on prompt instructions to prevent loops.")
    print('  "Stop trying if it fails" in a system prompt is NOT a control.')
    print("  Enforce max_iterations in the agent harness or orchestration code.")


def show_prompt_caching():
    """Prompt caching reduces token costs for repeated prefixes."""
    print_section("Token Optimization — Prompt Caching")

    print("  Prompt caching stores frequently-used prompt prefixes:")
    print("  - System prompts (reused across all requests)")
    print("  - Tool definitions (reused across all tool calls)")
    print("  - Few-shot examples (reused across similar requests)")
    print()
    cached_tokens, fresh_tokens = 800, 200
    without_caching = (cached_tokens + fresh_tokens) / 1000 * PRICE_PER_1K_INPUT_TOKENS
    with_caching = (fresh_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS + (cached_tokens / 1000) * (PRICE_PER_1K_INPUT_TOKENS * 0.125)
    savings_pct = (1 - with_caching / without_caching) * 100
    print(f"  Savings example ({cached_tokens} cached + {fresh_tokens} fresh input tokens):")
    print(f"  - Without caching: ${without_caching:.6f} per request")
    print(f"  - With caching:    ${with_caching:.6f} per request")
    print(f"  - Computed savings: {savings_pct:.0f}% on input token costs for this prefix mix")
    print()
    print("  NOTE: Prompt caching is an instructor talking point.")
    print("  Students do not configure caching in the 4-hour lab.")


def main():
    print("Cost Controls and Runaway Prevention — Instructor Demo\n")

    show_cost_dimensions()
    show_idle_timeout()
    show_runaway_execution()
    show_prompt_caching()

    print_section("Key Takeaways")
    print("  1. Agent costs span Runtime, LLM, Gateway, and Memory dimensions — compute, don't guess")
    print("  2. Proactively stop sessions; idle-timeout and max-lifetime are backstops, not a plan")
    print("  3. max-iterations and harness-timeout are infrastructure controls, not prompts")
    print("  4. Circuit breakers halt cascading failures at the Gateway layer")
    print("  5. Prompt caching's savings depend on how much of the prefix is actually cached")


if __name__ == "__main__":
    main()
