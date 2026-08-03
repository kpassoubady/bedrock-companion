# Concept: Core Execution (Runtime and Gateway)

To build secure, production-grade agentic systems, you must decouple the execution environment (Runtime) from the integration access layer (Gateway). This separation allows you to scale agent capacity without exposing internal backend tools directly to the execution environment.

## AgentCore Runtime

The AgentCore Runtime provides a serverless execution environment specifically designed for hosting agent and tool code.

*   **Session Isolation:** The primary security boundary is the dedicated microVM allocated for each user session. This prevents cross-tenant data leakage and ensures that the agent's state is completely isolated.
*   **Scale and Flexibility:** It is designed for both real-time interactions with fast cold starts and asynchronous, long-running agent workloads that can operate for hours.
*   **Execution Role Boundaries:** While Runtime isolates the compute session, the code inside the microVM runs under a specified IAM execution role. This role must be tightly scoped to least privilege. Using an overly broad development policy in production expands the blast radius if the agent is hijacked.
*   **Tenant Mapping:** Session isolation does not authenticate the caller. Your application backend must validate the user and map them to a session ID before invoking the Runtime.

## AgentCore Gateway

The Gateway is a centralized, governed integration layer that connects agents to external tools, other agents, and foundation models.

*   **Protocol Transformation:** Gateway converts existing enterprise assets—such as REST APIs, OpenAPI specifications, and AWS Lambda functions—into standardized Model Context Protocol (MCP) compatible tools.
*   **Tool Governance:** By fronting services with Gateway, developers manage tool access through a single governed endpoint rather than hardcoding point-to-point API integrations directly in the agent code.
*   **Not a Public Edge:** AgentCore Gateway is agent-facing and tool-aware. It does not replace the public API edge (like Amazon API Gateway or a backend-for-frontend), which remains responsible for client authentication, throttling, WAF integration, and request validation.

## Architectural Implications

When architecting production agents, apply the following principles:

1.  **Do not conflate session isolation with tenant isolation.** The application owns the user-to-session mapping.
2.  **Tool calls do not bypass authorization.** A valid tool call routed through Gateway is not proof that the caller is allowed to perform the action. Downstream services must re-verify authorization.
3.  **Assume component failure.** Runtime, Gateway, models, and downstream APIs can fail independently. Implement bounded retries and timeouts.
4.  **Enforce bypass prevention.** Use resource policies or IAM conditions to prevent callers from bypassing the Gateway and invoking Runtime tools directly.

### Component Comparison

| Capability | Role | Security Focus |
| :--- | :--- | :--- |
| **Runtime** | Executes agent code in a microVM. | Scope the IAM execution role strictly; do not use broad access policies. |
| **Gateway** | Routes tool calls and translates protocols. | Allowlist tools; ensure downstream targets enforce business logic authorization. |
