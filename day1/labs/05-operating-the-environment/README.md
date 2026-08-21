# Lab 05: Deploy and Inspect a Governed Agent

Operate a pre-configured AgentCore application that uses a Salesforce service-case scenario and a retail order-status tool. The exercise performs real AWS operations. It never prints simulated success.

## Goal

Produce evidence for five boundaries:

1. The assigned Runtime reaches `READY` after a create or update.
2. The restricted execution role is attached to that Runtime.
3. A SigV4-signed call reaches the pre-created read-only Gateway tool.
4. Two different Runtime sessions retrieve one AgentCore Memory session.

## Time Budget

| Activity | Minutes |
| :--- | ---: |
| Read the architecture and run preflight | 5 |
| Compare the broad and restricted policies | 5 |
| Implement the agent logic | 5 |
| Deploy or update the assigned Runtime | 5 |
| Check the retail Gateway tool | 5 |
| Verify Salesforce case continuity in Memory | 5 |
| Production-boundary share-out and buffer | 10 |
| **Total** | **45** |

Work in pairs. One person drives for deployment and Gateway checks; switch drivers before the Memory and trace checks.

## Prerequisites

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/labs/05-operating-the-environment/start/05-operating-the-environment.ipynb)


- Python 3.10 or later
- AWS CLI configured for the assigned sandbox
- Packages installed with `python3 -m pip install -r requirements.txt`
- Instructor-provided Runtime artifact, Gateway, Memory, role, policy, and team-specific values

Do not use real Salesforce records, customer identifiers, or order data. The supplied targets return synthetic fixtures.

## Load Your Team Credentials

The instructor sent you a presigned S3 link to `team-XX.env` (see `bedrock-lab-provision`'s `docs/credential-distribution.md` for how it was sent). This section is the only place you export environment variables — complete all of it before Checkpoint 1.

1. Save `team-XX.env` outside this repo — for example, your home directory. Never copy it into `bedrock-companion`: this repo's `.gitignore` only ignores a file literally named `.env`, so `team-XX.env` would not be excluded and is one `git add` away from being committed with a live AWS access key, secret key, and console password.
2. Load it into your shell:

   ```bash
   source ~/team-XX.env
   ```

3. Confirm the credentials are active and belong to your team:

   ```bash
   aws sts get-caller-identity
   ```

4. `team-XX.env` sets `AWS_DEFAULT_REGION`, but the scripts in this lab read `AWS_REGION` specifically. Export it too so the two agree, and export the remaining values the instructor gives you separately — `team-XX.env` does not include these:

   ```bash
   export AWS_REGION=us-east-1
   export AGENT_NAME=sf_case_team01_am   # letters, digits, underscores only; append _am/_pm if the instructor asks
   export S3_KEY=<instructor-provided>
   export GATEWAY_URL=<instructor-provided>
   export GATEWAY_TOOL_NAME=<instructor-provided>
   export MEMORY_ID=<instructor-provided>
   export ACTOR_ID=<instructor-provided>   # optional — a random value is generated if unset
   export MEMORY_SESSION_ID=<instructor-provided>  # optional — a random value is generated if unset
   export ORDER_ID=<instructor-provided>
   export EXPECTED_ORDER_STATUS=<instructor-provided>
   export AGENT_RUNTIME_ID=
   export AGENT_RUNTIME_ARN=
   ```

   **Do not re-export `EXECUTION_ROLE_ARN` or `S3_BUCKET`.** `team-XX.env` already set them correctly for your team. Re-exporting them from any other source — including an old copy of this doc's example values — overwrites the real role/bucket with a placeholder and Checkpoint 1 fails with `AccessDenied`.

   `GATEWAY_TOOL_NAME` looks unusual — it is the target name and the tool name joined with three underscores, e.g. `LabAgent-TeamXX-OrderStatusTarget___OrderStatus_TeamXX`. AgentCore Gateway namespaces every Lambda-backed tool this way in `tools/list` and `tools/call`; the shorter name registered when the tool was created is never callable on its own. Use the exact value the instructor gives you — do not shorten it.
5. The console sign-in block appended at the end of `team-XX.env` is for Checkpoint 6 (CloudWatch trace inspection). You won't need it until then.

Set `AGENT_RUNTIME_ID` when updating an assigned Runtime. After deployment, export the actual `AGENT_RUNTIME_ARN` printed by the script.

## Checkpoint 1: Identity and Policy

```bash
aws sts get-caller-identity
aws iam get-role --role-name "${EXECUTION_ROLE_ARN##*/}"
aws iam list-role-policies --role-name "${EXECUTION_ROLE_ARN##*/}"
aws iam get-role-policy --role-name "${EXECUTION_ROLE_ARN##*/}" --policy-name AgentCoreExecutionPolicy
```

Confirm `AgentCoreExecutionPolicy` is listed and its document scopes the role to only the assigned model, Gateway, Memory, and telemetry actions. Provisioning attaches this as an inline role policy, not a managed one — `aws iam list-attached-role-policies` will always return an empty list for this role by design, so it does not confirm anything here. The lab invoker needs both `bedrock-agentcore:InvokeAgentRuntime` and `bedrock-agentcore:InvokeAgentRuntimeForUser` because the checkpoint supplies `runtimeUserId`. `bedrock-agentcore:InvokeGateway` applies to a Gateway; `bedrock-agentcore:InvokeAgentRuntime` applies to a Runtime.

If `AgentCoreExecutionPolicy` is missing, ask the instructor to re-run provisioning for your team — students are not granted `iam:PutRolePolicy` on this role, so you cannot attach or repair it yourself.

## Checkpoint 2: Implement the Agent Logic

Before deploying, open `start/agent.py` and complete the three TODOs:

1. `call_gateway_tool`: Invoke the Gateway MCP tool using SigV4Auth and urllib.request.
2. `load_memory_turns`: Retrieve conversation history from AgentCore Memory using `agentcore.list_events`.
3. `write_memory_turn`: Write new messages to AgentCore Memory using `agentcore.create_event`.

**Developer Prompt:**

If you are using a coding assistant, you can use the following prompt to help solve the TODOs:

```text
Complete the three TODOs in start/agent.py. Use boto3 SigV4Auth and urllib.request 
for the Gateway tool call. Use the bedrock-agentcore boto3 client for list_events and 
create_event. Ensure the returned memory turns are formatted correctly for the Bedrock Converse API.
```

## Checkpoint 3: Deploy or Update

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

The script also writes `deploy.env` in the current directory with `AGENT_RUNTIME_ID`, `AGENT_RUNTIME_VERSION`, and `AGENT_RUNTIME_ARN` from this run. Load it instead of copy-pasting the printed values:

```bash
source deploy.env
```

Re-running `deploy_agent.py` for the same `AGENT_NAME` finds and updates the existing Runtime automatically — you do not need to export `AGENT_RUNTIME_ID` yourself first.

## Checkpoint 4: Invoke the Retail Gateway Tool

```bash
python3 check_gateway.py
```

Expected marker:

```text
GATEWAY_OK
```

The script signs a direct MCP `tools/call` checkpoint with the current student IAM identity. It validates the JSON-RPC request ID, rejects top-level and `isError` failures, and requires both `ORD-1001` and the expected status. This checkpoint tests Gateway independently before Runtime uses the same tool.

## Checkpoint 5: Verify AgentCore Memory

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

> CloudWatch trace inspection is skipped for this class — students do not currently have console access. This checkpoint will return once that access is available.

## Definition of Done

- Actual Runtime ID, version, ARN, and `READY` status
- Restricted policy attached to the prepared role
- `GATEWAY_OK` for the synthetic retail order
- `CONTINUITY_OK` for the synthetic Salesforce case
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

## Reference: Environment Variables

For awareness only — do not run this as a block. Doing so re-exports placeholder values over the real ones from `team-XX.env` and breaks the checkpoints.

| Variable | Source |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` | `team-XX.env` |
| `EXECUTION_ROLE_ARN`, `S3_BUCKET` | `team-XX.env` — never re-export |
| `AWS_REGION`, `AGENT_NAME`, `S3_KEY`, `GATEWAY_URL`, `GATEWAY_TOOL_NAME`, `MEMORY_ID`, `ORDER_ID`, `EXPECTED_ORDER_STATUS` | Instructor-provided; exported by you in "Load Your Team Credentials" |
| `ACTOR_ID`, `MEMORY_SESSION_ID` | Instructor-provided, but optional — `verify_memory.py` generates a random value if unset |
| `AGENT_RUNTIME_ID`, `AGENT_RUNTIME_ARN` | Empty until deployment; `AGENT_RUNTIME_ARN` set from the script's printed output after Checkpoint 3 |
