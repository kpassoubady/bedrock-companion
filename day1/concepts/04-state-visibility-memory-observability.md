# Concept: State and Visibility (Memory and Observability)

Production agent systems require state to act intelligently over time, and observability to understand their reasoning. Amazon Bedrock AgentCore provides managed infrastructure for both, but application teams retain responsibility for data governance, security policies, and incident response.

## AgentCore Memory

AgentCore Memory allows agents to maintain context across conversational turns and discrete sessions. It is fundamentally divided into two types:

1. **Short-Term Memory:** Stored events grouped by `actorId` and `sessionId`. Event retention and deletion follow the Memory configuration and application governance; session completion does not imply immediate deletion.
2. **Long-Term Memory:** Extracted records that can span sessions. Their lifecycle is controlled by strategies, namespaces, retention, and deletion policy rather than assumed indefinite storage.

### Five Long-Term Memory Strategies

AgentCore provides five configurable strategies for extracting durable knowledge from raw events:

- **Semantic:** Extracts key facts, entities, and relationships (general-purpose).
- **Summarization:** Creates compressed conversation summaries, preventing the need to store raw event logs.
- **User Preference:** Infers and explicitly stores personal preferences (e.g., tone, formatting, domain-specific defaults).
- **Episodic:** Records sequences of events to support temporal reasoning ("what happened when").
- **Custom:** Developer-defined extraction logic for domain-specific needs.

### Actor and Session Scoping

AgentCore Memory uses an `actorId` and a `sessionId` to organize events. Long-term records also use configured namespaces. These identifiers are partition keys, not authorization controls; the application and IAM/resource policies must prevent a caller from selecting another actor or tenant namespace.

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

## Security Implications

This architecture addresses memory poisoning from the **OWASP Top 10 for Agentic Applications (2026)** and supports broader detection and response controls:

- **ASI06: Memory & Context Poisoning:** An agent's stored state influences its future reasoning. A known attack, *MemoryTrap*, demonstrated that untrusted input (like a compromised GitHub repo) could be written to an agent's memory, eventually altering its system-level behavior in future sessions. Treat memory as an attack vector. Only promote trusted data to long-term memory, and maintain audit trails of memory writes.
- **Observable execution:** ASI09 is Human-Agent Trust Exploitation, not an observability category. Comprehensive, access-controlled telemetry still helps detect goal hijacking, memory poisoning, tool misuse, and cascading failures.
