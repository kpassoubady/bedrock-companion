# Lab 05: Operating the Environment

Welcome to the Day 1 Breakout Lab. Deploy a pre-built AgentCore agent and verify its identity, memory, and observability features.

## Prerequisites

- AWS CLI configured with your sandbox credentials
- Python 3.10+ with boto3 installed
- Instructor-provided: execution role ARN, S3 bucket name, team prefix

## Lab Tasks

1. **Identify components** on the architecture diagram (slide deck)
2. **Compare IAM policies** — review the broad vs. restricted policy (instructor will show `demo-least-privilege-iam.py`)
3. **Deploy the agent** — run `python3 deploy_agent.py`
4. **Invoke through Gateway** — run `python3 verify_memory.py` (first invocation)
5. **Verify memory continuity** — second invocation with same actorId + sessionId
6. **Inspect the trace** — navigate to CloudWatch → Generative AI Observability → AgentCore

## Instructions

### 1. Deploy

```bash
cd start/
python3 deploy_agent.py
```

Fill in the TODO values before running: execution role ARN, S3 bucket, agent name (use your team prefix).

### 2. Verify Memory

```bash
python3 verify_memory.py
```

This sends two invocations with the same `actorId` and `sessionId`. The second invocation should recall context from the first.

### 3. Inspect Traces

1. Open the AWS Console → **CloudWatch**
2. Navigate to **Generative AI Observability** → **AgentCore** tab
3. Find your traces by session ID (printed by verify_memory.py)
4. Record: total latency, input/output tokens, tool calls, memory operations, errors

## Solution

If you get stuck, refer to the complete examples in the `solution/` directory.

## Concept Reference

After the lab, review the concept docs in `day1/concepts/` for deeper understanding of each topic.
