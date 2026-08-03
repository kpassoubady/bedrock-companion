# Concept: AgentCore Architecture Overview

Amazon Bedrock AgentCore is a modular managed platform designed for building, deploying, and operating agents securely at scale. The platform allows development teams to adopt its services independently and supports multiple agent frameworks and foundation models. Framework portability reduces coupling at the agent-code layer; however, identity configuration, memory schemas, and gateway integrations remain platform-specific architectural components.

## The Five Focus Capabilities

This course focuses on five key capabilities of AgentCore that enable production-ready agent deployment:

1. **AgentCore Runtime**: A secure, serverless hosting environment built for agent and tool code. It provides dedicated microVM isolation for each session, supporting both synchronous and asynchronous workloads. While Runtime isolates compute sessions, the application backend must enforce the mapping between an authenticated user and their session ID.
2. **AgentCore Gateway**: A standardized entry point for agents to discover and invoke tools or models. It handles Model Context Protocol (MCP) translation and direct HTTP routing. Gateway is agent-facing and tool-aware, distinct from Amazon API Gateway, which manages public client traffic.
3. **AgentCore Identity**: Manages inbound agent authentication and outbound access to services. It integrates with identity providers and uses IAM SigV4 for service-to-service access. Identity propagation alone does not grant authorization; systems must combine verified identity with least-privilege IAM policies.
4. **AgentCore Memory**: Supplies state for context-aware behavior through short-term conversational memory and long-term storage across sessions. Production memory stores require tenant partitioning, retention policies, and strategies for handling stale or poisoned data.
5. **AgentCore Observability**: Delivers agent-specific tracing, metrics, and logs. It provides CloudWatch-backed telemetry for token use, latency, and tool invocations. Teams must still define service-level objectives, alarms, and incident-response workflows.

## Practical Implications

Deploying an agent on managed infrastructure provides scalability and security baselines, but it does not automatically make the agent's behavior safe or compliant. Teams must maintain governance over the end-to-end request lifecycle.

For example, execution-role credentials are accessible to the code running inside a Runtime session. Providing an overly broad IAM policy during development is a common mistake. Production deployments require a tightly scoped execution role that grants access only to the specific resources the agent needs.

Similarly, valid tool calls through the Gateway do not guarantee safety. Downstream systems must enforce authorization and validate business rules independently. Consequential writes, such as modifying a database or sending an email, require idempotency controls, explicit user approval, and comprehensive audit logging.

## Core Component Comparison

| Component | Primary Function | Boundary / Limitation |
| :--- | :--- | :--- |
| **Runtime** | Executes agent code in isolated sessions. | Does not authenticate users; application backend owns user-to-session mapping. |
| **Gateway** | Routes agent requests to tools and models. | Does not replace API Gateway for edge routing or client-facing validation. |
| **Identity** | Manages authentication and credentials. | Identity propagation is not authorization; least-privilege IAM is still required. |
| **Memory** | Stores short-term and long-term state. | Requires explicit tenant partitioning and data lifecycle management. |
| **Observability** | Tracks metrics, logs, and traces. | Requires configured alarms and data governance for sensitive payload data. |

Understanding these components and their architectural boundaries ensures a clear separation between control, data, and governance concerns in production systems.
