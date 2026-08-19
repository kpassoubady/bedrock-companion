# Lab 01: Send Your First Amazon Bedrock Request

Use the OpenAI Python SDK with Amazon Bedrock's OpenAI-compatible Chat Completions API. You will complete a small request function, prove its behavior with offline acceptance tests, and then send one live question to a low-cost model.

## Scenario and Goal

Your team is validating model connectivity before placing an application inside AgentCore Runtime. Build the smallest reliable request path that keeps the endpoint, API key, prompt, and model choice explicit.

By the end of the lab, `bedrock_first_request.py` must print a non-empty answer from Amazon Bedrock and this marker:

```text
MODEL_RESPONSE_OK model=openai.gpt-oss-20b-1:0
```

## Objectives

- Configure the regional `bedrock-runtime` OpenAI-compatible endpoint.
- Call the Chat Completions API through `client.chat.completions.create`.
- Separate model configuration from request logic.
- Reject invalid input and empty model output before reporting success.

## Time Budget

| Activity | Minutes |
| :--- | ---: |
| Read, predict, and install | 4 |
| Run the failing acceptance check | 2 |
| Implement and review the request | 7 |
| Run one live request | 4 |
| Share evidence | 3 |
| **Total** | **20** |

Work in pairs. Privately predict which values the OpenAI SDK reads from the environment, then compare answers. One person drives through the offline tests; switch drivers before the live request.

## Prerequisites

- Python 3.10 or later
- An instructor-approved AWS Region in which `openai.gpt-oss-20b-1:0` is available
- A short-term Amazon Bedrock API key

Use only a short-term lab key. Store it only in this lab's local `.env`, which Git ignores. Do not put it in source code, `.env.example`, shell history, screenshots, or chat. Never commit or share `.env`. In production, do not manually distribute keys; use an IAM role or temporary AWS credentials with a supported token-refresh or AWS SDK authentication flow.

## Setup

From this lab directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

Open `.env` in your editor. Replace the dummy Region and key while preserving the variable references:

```dotenv
AWS_REGION=<instructor-provided-region>
AWS_BEARER_TOKEN_BEDROCK=<your-short-term-Bedrock-API-key>
OPENAI_API_KEY=${AWS_BEARER_TOKEN_BEDROCK}
OPENAI_BASE_URL=https://bedrock-runtime.${AWS_REGION}.amazonaws.com/openai/v1
```

`python-dotenv` loads this lab-level file before creating the client. `OPENAI_API_KEY` references the same token as `AWS_BEARER_TOKEN_BEDROCK`, so you enter the key only once. The real `.env` is ignored by Git; `.env.example` contains dummy values and is safe to commit.

The requirements follow the AWS quickstart and install `boto3`, `openai`, and `python-dotenv`. This exercise sends the request through the OpenAI SDK; later course code uses `boto3` for Bedrock and AgentCore APIs.

Enter the starter directory after saving `.env`:

```bash
cd start
```

## Baseline and First Failing Check

Confirm that the starter imports and compiles:

```bash
python3 -m py_compile bedrock_first_request.py test_bedrock_first_request.py
```

Run the offline acceptance check. It uses a fake client, consumes no key or model tokens, and should initially fail at `TODO 1`:

```bash
python3 -m unittest -v
```

Do not delete, skip, weaken, or rewrite the acceptance tests to make them pass.

## Technical Task

Edit only `start/bedrock_first_request.py`. Complete `ask_bedrock` so that it:

1. Rejects a blank prompt with `ValueError("prompt must not be empty")` without sending a request.
2. Calls `client.chat.completions.create` exactly once with the supplied `model_id` and the `prompt` wrapped in a single user message.
3. Reads `response.choices[0].message.content`, strips any `<reasoning>...</reasoning>` block the model may prepend, and strips whitespace.
4. Raises `RuntimeError` containing `empty text response` when no text remains.
5. Returns the non-empty answer.

Preserve `DEFAULT_MODEL_ID`, the function signature, environment validation, dependencies, and tests. Do not print or log the API key.

## Bounded Developer Prompt

```text
I am working in a Python 3.10+ course project using openai 2.37.0, boto3 1.43.62, and python-dotenv 1.2.2. Read start/bedrock_first_request.py and start/test_bedrock_first_request.py. Implement only TODO 1 in ask_bedrock. Preserve DEFAULT_MODEL_ID, the function signature, .env loading, environment validation, dependencies, tests, and formatting. Do not weaken or change the tests, add dependencies, expose credentials, or rewrite unrelated code. The function must reject a blank prompt without a request, call client.chat.completions.create exactly once with model and a single user message containing the prompt, strip any <reasoning>...</reasoning> block and whitespace from response.choices[0].message.content, and reject empty output. Explain the proposed change, run python3 -m unittest -v from start/, and report the result.
```

Before applying a coding assistant's proposal, verify that the API call uses the injected `client`, not a second client created inside `ask_bedrock`. Explain why that choice keeps the acceptance check offline and makes the request path testable.

## Verify and Run

Run the focused check until all seven tests pass:

```bash
python3 -m unittest -v
```

Then send one live request:

```bash
python3 bedrock_first_request.py
```

A successful run prints the model's answer followed by `MODEL_RESPONSE_OK`. Model wording is nondeterministic, so the evidence is a non-empty answer and the success marker, not an exact sentence.

If the live call fails, preserve the exact error and use this repair prompt:

```text
Here is the exact failure from python3 bedrock_first_request.py: <paste failure>. Read start/bedrock_first_request.py and the failing acceptance check. Identify whether the root cause is environment configuration, regional model availability, authentication, or request logic. Propose the smallest correction, preserve the acceptance contract, rerun python3 -m unittest -v, and name the criterion restored. Do not print or request the API key.
```

After the lab, delete the local `.env` or remove its key value. Keep `.env.example` so the setup pattern remains available. If you previously exported either token in your shell, also run:

```bash
unset OPENAI_API_KEY AWS_BEARER_TOKEN_BEDROCK
```

## Completion Levels

- **Basic:** All seven offline tests pass and the function uses the required model and Responses API shape.
- **Intermediate:** One live request prints a non-empty answer and `MODEL_RESPONSE_OK`.
- **Stretch:** Change only `DEFAULT_PROMPT`, ask a question tied to Runtime or Gateway, and explain why prompt changes should not require endpoint or authentication changes.

## Definition of Done

- `python3 -m py_compile bedrock_first_request.py test_bedrock_first_request.py` succeeds.
- `python3 -m unittest -v` reports seven passing tests.
- One live invocation prints a non-empty response and the expected marker.
- No credential appears in code, test output, screenshots, or the shared artifact.
- The pair can explain why `bedrock-runtime` and AgentCore Runtime are different services.

## Share-Out

Show the success marker and one sentence from the response. In one minute, explain where you kept the model and endpoint configurable, why the injected client matters for testing, and one production authentication change you would make.

If you remain blocked after checking the tests, exact error, Region, endpoint, and instructor guidance, compare your implementation with `solution/` without copying credentials or unrelated code.

## References

- [Amazon Bedrock quickstart](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)
- [OpenAI gpt-oss-20b model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-20b.html)
