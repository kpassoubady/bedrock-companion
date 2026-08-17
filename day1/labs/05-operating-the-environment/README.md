# Lab 05: Deploy and Inspect a Governed Agent

Operate a pre-configured AgentCore application that uses a Salesforce service-case scenario and a retail order-status tool. The exercise performs real AWS operations. It never prints simulated success.

## Goal

Produce evidence for five boundaries:

1. The assigned Runtime reaches `READY` after a create or update.
2. The restricted execution role is attached to that Runtime.
3. A SigV4-signed call reaches the pre-created read-only Gateway tool.
4. Two different Runtime sessions retrieve one AgentCore Memory session.
5. CloudWatch shows the Runtime, model, tool, Memory, status, and latency evidence.

## Time Budget

| Activity | Minutes |
| :--- | ---: |
| Read the architecture and run preflight | 5 |
| Compare the broad and restricted policies | 5 |
| Deploy or update the assigned Runtime | 8 |
| Check the retail Gateway tool | 5 |
| Verify Salesforce case continuity in Memory | 8 |
| Inspect the trace and record evidence | 9 |
| Production-boundary share-out and buffer | 5 |
| **Total** | **45** |

Work in pairs. One person drives for deployment and Gateway checks; switch drivers before the Memory and trace checks.

## Prerequisites

- Python 3.10 or later
- AWS CLI configured for the assigned sandbox
- Packages installed with `python3 -m pip install -r requirements.txt`
- CloudWatch Transaction Search enabled before class
- Instructor-provided Runtime artifact, Gateway, Memory, role, policy, and team-specific values

Do not use real Salesforce records, customer identifiers, or order data. The supplied targets return synthetic fixtures.

## Configuration

Export the values supplied by the instructor. Use a cohort-specific suffix such as `_am` or `_pm` to prevent collisions.

```bash
export AWS_REGION=us-west-2
export AGENT_NAME=sf_case_team01_am
export EXECUTION_ROLE_ARN=arn:aws:iam::123456789012:role/assigned-runtime-role
export RESTRICTED_POLICY_ARN=arn:aws:iam::123456789012:policy/assigned-runtime-policy
export S3_BUCKET=assigned-agentcore-artifacts
export S3_KEY=course/agent/deployment_package.zip
export GATEWAY_URL=https://assigned-gateway.example.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
export GATEWAY_TOOL_NAME=retail___get_order_status
export MEMORY_ID=assigned-memory-id
export ACTOR_ID=team01_am
export MEMORY_SESSION_ID=sf-case-team01-am
export ORDER_ID=ORD-1001
export EXPECTED_ORDER_STATUS=SHIPPED
# keep empty the below 2 values
export AGENT_RUNTIME_ID=
export AGENT_RUNTIME_ARN=
```

`AGENT_NAME` may contain only letters, digits, and underscores and must start with a letter. Set `AGENT_RUNTIME_ID` when updating an assigned Runtime. After deployment, export the actual `AGENT_RUNTIME_ARN` printed by the script.

## Checkpoint 1: Identity and Policy

```bash
aws sts get-caller-identity
aws iam get-role --role-name "${EXECUTION_ROLE_ARN##*/}"
aws iam list-attached-role-policies --role-name "${EXECUTION_ROLE_ARN##*/}"
```

Confirm that `RESTRICTED_POLICY_ARN` is attached. The Runtime role needs only the assigned model, Gateway, Memory, and telemetry actions. The lab invoker needs both `bedrock-agentcore:InvokeAgentRuntime` and `bedrock-agentcore:InvokeAgentRuntimeForUser` because the checkpoint supplies `runtimeUserId`. `bedrock-agentcore:InvokeGateway` applies to a Gateway; `bedrock-agentcore:InvokeAgentRuntime` applies to a Runtime.

If the supplied policy is not attached, use the instructor-approved command:

```bash
aws iam attach-role-policy \
  --role-name "${EXECUTION_ROLE_ARN##*/}" \
  --policy-arn "$RESTRICTED_POLICY_ARN"
```

## Checkpoint 2: Deploy or Update

```bash
cd start
python3 deploy_agent.py
```

Expected terminal markers:

```text
DEPLOYMENT_WAIT: status=READY
DEPLOYMENT_OK
AGENT_RUNTIME_ID=...
AGENT_RUNTIME_VERSION=...
AGENT_RUNTIME_ARN=...
```

The script validates the S3 ZIP, performs a real create or update, waits up to five minutes, and exits nonzero on failure. `update_agent_runtime` moves `DEFAULT` to the new version automatically, so this classroom path is permitted only in the assigned sandbox. Production promotion uses named endpoints and `update_agent_runtime_endpoint` after evaluation.

## Checkpoint 3: Invoke the Retail Gateway Tool

```bash
python3 check_gateway.py
```

Expected marker:

```text
GATEWAY_OK
```

The script signs a direct MCP `tools/call` checkpoint with the current student IAM identity. It validates the JSON-RPC request ID, rejects top-level and `isError` failures, and requires both `ORD-1001` and the expected status. This checkpoint tests Gateway independently before Runtime uses the same tool.

## Checkpoint 4: Verify AgentCore Memory

```bash
python3 verify_memory.py
```

Expected markers:

```text
RUNTIME_OK
TOOL_OK
MEMORY_OK
CONTINUITY_OK
```

The first Runtime invocation calls the retail order tool and writes Salesforce case context. The second uses a different Runtime session ID with the same Memory `actorId` and `sessionId`, then the script calls `ListEvents`. This produces one Runtime trace with model, Gateway tool, and Memory activity while distinguishing AgentCore Memory continuity from one warm microVM.

Actor and session IDs organize Memory data. They are not authorization controls by themselves; the application and IAM policy must prevent identifier spoofing.

## Checkpoint 5: Inspect CloudWatch

Open **CloudWatch > GenAI Observability > Amazon Bedrock AgentCore > Traces**. Use the Runtime session IDs printed by `verify_memory.py` and record:

| Signal | Evidence |
| :--- | :--- |
| Runtime status and total latency | |
| Model and token data | |
| Gateway tool name and status | |
| Memory read/write activity | |
| Output-validation result | |
| Error or success status | |

Trace ingestion can be delayed. If the live trace is not visible after the instructor's wait limit, use the instructor-provided redacted trace captured from the same lab version. Label fallback evidence clearly; do not claim it came from your invocation.

## Definition of Done

- Actual Runtime ID, version, ARN, and `READY` status
- Restricted policy attached to the prepared role
- `GATEWAY_OK` for the synthetic retail order
- `CONTINUITY_OK` for the synthetic Salesforce case
- Live or clearly labeled fallback trace evidence
- One-minute explanation of controls still outside this lab: caller authorization, tenant mapping, approval for writes, idempotency, bounded retries, data deletion, staged rollout, rollback, budgets, and incident ownership

## Developer Prompt

```text
I am working in a Python 3.10+ Amazon Bedrock AgentCore course project. Read
README.md and the three scripts in start/. Diagnose only the exact failing
checkpoint. Preserve the environment-variable contract, AWS API calls, assertions,
and nonzero failure behavior. Do not replace AWS calls with mocks, weaken checks,
or edit files outside this lab. Run python3 -m compileall -q start and explain which
acceptance criterion your smallest proposed correction restores.
```

## Help Order

1. Read the categorized error: `CONFIG`, `IAM`, `DEPLOYMENT`, `GATEWAY`, `MEMORY`, or `CONTINUITY`.
2. Compare the command and environment values with the instructor handout.
3. Ask your partner, then another group.
4. Ask the instructor for the known-good checkpoint output.
5. Compare with `solution/` without copying unrelated changes.
