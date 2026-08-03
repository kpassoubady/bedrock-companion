# Concept: Securing the Agent with Identity

Autonomous agents pose a unique security challenge: they aggregate permissions across multiple tools and environments. A compromised agent can exploit any credential it holds. To manage this "attribution gap," Amazon Bedrock AgentCore provides a specialized credential management layer.

## The Three-Identity Separation Model

In a production environment, an agentic request traverses at least three distinct identities. Understanding this separation is critical to securing your architecture:

1. **Caller Identity:** This represents the human user or upstream system initiating the request. The caller is authenticated at the public edge (e.g., API Gateway, backend-for-frontend) via standard providers like Amazon Cognito, Okta, or Entra ID. This identity answers: *Who initiated this request?*
2. **Workload Identity:** This is the IAM execution role under which the agent code runs inside the AgentCore Runtime microVM. It governs the infrastructure actions the agent is permitted to perform, such as emitting logs or invoking the Gateway. It must *never* be a broad development role (like `bedrock:*`).
3. **Downstream Credential:** When the agent invokes a tool via AgentCore Gateway, it presents this credential to the target service. It may be an IAM SigV4 signature for AWS services or a scoped OAuth token. It answers: *What business data can the agent access?*

Conflating these three identities—such as embedding a user's API key directly into the agent's prompt or using a shared service account for all users—creates significant security vulnerabilities.

## Agent Identity Directory

The **Agent Identity Directory** serves as a centralized, account-wide registry for agent and workload identities. It replaces scattered static service accounts with environment-agnostic workload identities that support dynamic, autonomous operations.

By leveraging the Agent Identity Directory, organizations can issue short-lived, task-scoped tokens. This reduces credential exposure and limits the blast radius if an agent is hijacked or behaves unexpectedly.

## Addressing Agentic Security Risks (OWASP)

AgentCore Identity maps directly to the mitigation of critical risks outlined in the **OWASP Top 10 for Agentic Applications**:

- **ASI03: Identity and Privilege Abuse:** This is the foundational risk. Agents are identity aggregation points. If you compromise one agent with a broad IAM policy, you compromise every service it can touch. Mitigation requires strict separation of caller, workload, and downstream identities.
- **ASI01: Agent Goal Hijack:** Prompt injections can redirect an agent's plan. Deterministic IAM policies and scoped tokens prevent a hijacked agent from accessing unauthorized resources.
- **ASI10: Rogue Agents:** Excess autonomy is contained by enforcing capability manifests, egress network restrictions, and strict credential expiration.

Remember: **Deterministic external controls are the starting point for agentic security.** Do not rely on natural language prompts (e.g., "do not delete this database") for access control. Use IAM policies, scoped tokens, and approval gates to enforce security boundaries mathematically.
