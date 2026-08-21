"""
Demo — AgentCore Memory Continuity
Day 1 — Block 4: State and Visibility (Memory and Observability)

Demonstrates actor/session keying with a deterministic local event store.
This is an offline mechanism simulation, not an AgentCore Memory API call.
show_runtime_vs_memory_session() previews Breakout Lab task 5 by using two
different Runtime session IDs against the same Memory actorId/sessionId —
the same EVENT_STORE lookup the lab's verify_memory.py exercises for real.

No AWS credentials or API calls required.
Run: python3 day1/demos/demo-memory-continuity.py
"""
import json
import os
import time
import uuid

# --- Configuration ---
ACTOR_ID = os.environ.get("ACTOR_ID", "salesforce-user-123")
SESSION_ID = f"demo-session-{int(time.time())}"  # display label only; EVENT_STORE keys compare it as a plain string
EVENT_STORE = {}


def add_event(actor_id: str, session_id: str, role: str, content: str):
    EVENT_STORE.setdefault((actor_id, session_id), []).append({"role": role, "content": content})


def list_events(actor_id: str, session_id: str):
    return list(EVENT_STORE.get((actor_id, session_id), []))


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def explain_memory_types():
    """Explain the two memory types and five strategies."""
    print_section("AgentCore Memory Architecture")

    print("  Two memory types:")
    print("  - Short-Term Memory: Ephemeral dialogue within a single session")
    print("  - Long-Term Memory:  Facts, preferences, summaries persisted across sessions")
    print()
    print("  Five long-term memory strategies:")
    strategies = [
        ("Semantic", "Key facts, entities, relationships"),
        ("Summarization", "Compressed conversation summaries"),
        ("User Preference", "Tone, format, personal defaults"),
        ("Episodic", "Sequences of events (temporal reasoning)"),
        ("Custom", "Developer-defined extraction logic"),
    ]
    for name, desc in strategies:
        print(f"    {name:20s} — {desc}")
    print()
    print("  Scoping: actorId → actor-level isolation")
    print("           sessionId → session-level isolation")
    print(f"  Current: actorId={ACTOR_ID}, sessionId={SESSION_ID}")


def show_short_term_memory_flow():
    """Store and retrieve events with actor and session keys."""
    print_section("Short-Term Memory — Executable Local Model")

    first_message = "Salesforce case 00001042 is a high-priority portal access issue."
    add_event(ACTOR_ID, SESSION_ID, "USER", first_message)
    add_event(ACTOR_ID, SESSION_ID, "ASSISTANT", "I will retain that case context for this session.")
    same_session = list_events(ACTOR_ID, SESSION_ID)
    other_actor = list_events("salesforce-user-999", SESSION_ID)

    print(f"  Stored key: actorId={ACTOR_ID}, sessionId={SESSION_ID}")
    print(f"  Same key returned {len(same_session)} events:")
    for event in same_session:
        print(f"    {event['role']}: {event['content']}")
    print(f"  Different actor key returned {len(other_actor)} events.")
    print("  This separation is data organization, not authorization.")
    print("  The application and IAM policy must prevent actor ID spoofing.")


def show_runtime_vs_memory_session():
    """Preview Breakout Lab task 5: two different Runtime session IDs,
    same Memory actorId and Memory sessionId, verified with ListEvents.

    Runtime session IDs here are cosmetic labels for two separate
    invocations; the EVENT_STORE lookup that proves continuity is keyed
    only by (actorId, Memory sessionId) — exactly what the lab checks."""
    print_section("Runtime Session vs. Memory Session — Lab Task 5 Preview")

    runtime_session_a = f"runtime-{uuid.uuid4()}"
    runtime_session_b = f"runtime-{uuid.uuid4()}"
    memory_session_id = "case-00001042-continuity"

    print(f"  Runtime session A: {runtime_session_a}")
    add_event(ACTOR_ID, memory_session_id, "USER", "Case 00001042 needs a callback tomorrow.")
    after_a = list_events(ACTOR_ID, memory_session_id)
    print(f"    Wrote 1 event under Memory actorId={ACTOR_ID}, Memory sessionId={memory_session_id}")
    print(f"    ListEvents from Runtime session A: {len(after_a)} event(s)")

    print(f"\n  Runtime session B: {runtime_session_b} (a completely different Runtime session)")
    after_b = list_events(ACTOR_ID, memory_session_id)
    print(f"    ListEvents from Runtime session B, same Memory actorId/sessionId: {len(after_b)} event(s)")
    print(f"    Continuity holds: {after_a == after_b} (Runtime session ID never appeared in the lookup key)")
    print()
    print("  Runtime session ID and Memory sessionId are independent identifiers.")
    print("  Lab task 5 verifies this exact pattern with a real ListEvents call.")


def show_long_term_memory():
    """Explain how long-term memory persists across sessions.

    Students don't configure this in the 4-hour lab, but the instructor
    should explain the concept."""
    print_section("Long-Term Memory — Across Sessions (Instructor Narration)")

    print("  How long-term memory works:")
    print("  1. After each session, strategies extract durable knowledge")
    print("  2. Semantic: 'User prefers aisle seats'")
    print("  3. User Preference: 'User responds well to concise answers'")
    print("  4. Summarization: 'User booked 3 flights to Seattle in 2026'")
    print()
    print("  On next session (new sessionId, same actorId):")
    print("  - Short-term memory is empty (new session)")
    print("  - Long-term memory loads: preferences, facts, summaries")
    print("  - Agent: 'Welcome back! I see you often fly to Seattle.'")
    print()
    print("  NOTE: unlike the sections above, this is narration, not a computed local model.")
    print("  Long-term memory strategies are pre-configured in the lab; students do not implement them.")


def show_memory_governance():
    """Explain the shared responsibility boundary for memory.

    Memory is a data store — the application team owns governance."""
    print_section("Memory Governance — Shared Responsibility")

    governance = {
        "AgentCore manages": [
            "Memory infrastructure (storage, retrieval, embedding)",
            "Strategy execution (semantic extraction, summarization)",
            "actorId/sessionId scoping",
            "Encryption at rest (AWS KMS)",
        ],
        "You manage": [
            "Retention policies (how long to keep memories)",
            "PII redaction (before writing to memory)",
            "Deletion workflows (user-requested deletion, GDPR)",
            "Provenance tracking (which agent wrote which memory)",
            "Poisoned memory detection and quarantine",
            "Access control (which agents can read/write which namespaces)",
        ],
    }
    print(f"  {json.dumps(governance, indent=2)}")
    print()
    print("  OWASP ASI06 — Memory & Context Poisoning:")
    print("  - Treat memory as an attack surface")
    print("  - Validate writes before committing to long-term memory")
    print("  - Audit memory writes alongside agent invocations")
    print("  - Support memory quarantine and deletion")


def main():
    print("AgentCore Memory Continuity — Instructor Demo\n")

    explain_memory_types()
    show_short_term_memory_flow()
    show_runtime_vs_memory_session()
    show_long_term_memory()
    show_memory_governance()

    print_section("Key Takeaways")
    print("  1. actorId + sessionId scope short-term memory — same pair = continuity")
    print("  2. Different actorId separates records; authorization must prevent ID spoofing")
    print("  3. Runtime session IDs and Memory session IDs are independent — lab task 5 proves it")
    print("  4. Long-term memory persists across sessions using five strategies (narrated, not computed here)")
    print("  5. Memory is an attack surface (OWASP ASI06) — validate writes, audit access")


if __name__ == "__main__":
    main()
