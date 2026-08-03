# Concept: State and Visibility (Memory and Observability)

Production agent systems require state to act intelligently over time, and observability to understand their reasoning. Amazon Bedrock AgentCore provides managed infrastructure for both, but application teams retain responsibility for data governance, security policies, and incident response.

## AgentCore Memory

AgentCore Memory allows agents to maintain context across conversational turns and discrete sessions. It is fundamentally divided into two types:

1. **Short-Term Memory:** This captures the active, ephemeral dialogue within a single session. It maintains coherence during a specific task but does not persist once the session expires.
2. **Long-Term Memory:** This state persists across sessions, allowing the agent to remember facts, preferences, and past events indefinitely.

### Five Long-Term Memory Strategies

AgentCore provides five configurable strategies for extracting durable knowledge from raw events:

- **Semantic:** Extracts key facts, entities, and relationships (general-purpose).
- **Summarization:** Creates compressed conversation summaries, preventing the need to store raw event logs.
- **User Preference:** Infers and explicitly stores personal preferences (e.g., tone, formatting, domain-specific defaults).
- **Episodic:** Records sequences of events to support temporal reasoning ("what happened when").
- **Custom:** Developer-defined extraction logic for domain-specific needs.

### Actor and Session Scoping

Memory is intrinsically tied to identity. AgentCore Memory uses an `actorId` and a `sessionId` to partition data. Long-term retrieval is filtered by the `actorId` automatically, ensuring that one user's agent does not retrieve another user's stored preferences.

### The Shared Responsibility Boundary for Memory

AgentCore manages the extraction, embedding, and storage infrastructure. However, **you own the memory governance**. You must define retention schedules, PII redaction rules before storage, and processes for handling user-requested deletions. Memory is a data store subject to the same compliance frameworks as a database.

## AgentCore Observability

Observability in AgentCore moves beyond simple request-duration metrics. It uses OpenTelemetry (OTel) conventions to provide end-to-end distributed tracing.

### What a Trace Captures

A single agent request involves multiple steps (reasoning, tool calls, RAG lookups). Stage-level telemetry is crucial because a single high-latency request might be caused by a slow LLM, a throttled Gateway API, or a slow VectorDB lookup.

Key signals in a trace include:
- **`agent.run`**: The root span capturing the total time and final outcome of the request.
- **`gen_ai.client.operation`**: Child spans for each LLM invocation, capturing token consumption and model names.
- **`agent.tool_call`**: Child spans for Gateway tool invocations, showing the tool name and duration.

### Observability as a Security Control

Without comprehensive observability, defending against agent compromise is impossible. Traces provide the forensic evidence necessary to reconstruct the agent's decision-making process. Note that trace payloads can contain sensitive prompts and tool arguments, so redaction must occur at write time to prevent logs from becoming an attack surface.

## Security Implications: OWASP ASI06 and ASI09

This architecture directly addresses two critical risks from the **OWASP Top 10 for Agentic Applications (2026)**:

- **ASI06: Memory & Context Poisoning:** An agent's stored state influences its future reasoning. A known attack, *MemoryTrap*, demonstrated that untrusted input (like a compromised GitHub repo) could be written to an agent's memory, eventually altering its system-level behavior in future sessions. Treat memory as an attack vector. Only promote trusted data to long-term memory, and maintain audit trails of memory writes.
- **ASI09: Insufficient Observability:** This is a meta-category describing the absence of visibility. If you cannot see every reasoning step, tool invocation, and state transition, you cannot detect when ASI01 (Goal Hijack) or ASI06 (Memory Poisoning) occurs. Telemetry must be comprehensive and immutable.
