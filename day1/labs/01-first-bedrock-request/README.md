# Lab 01: Send Your First Amazon Bedrock Request

## Objectives

By the end of this lab you will be able to:

1. Configure the regional Amazon Bedrock OpenAI-compatible endpoint.
2. Send a Chat Completions request through the OpenAI Python SDK.
3. Validate prompts and reject empty model responses.
4. Keep credentials out of notebook source and output.

## Setup

You need an instructor-approved AWS Region where `openai.gpt-oss-20b-1:0` is available and a short-term Amazon Bedrock API key. The notebook prompts for the key with `getpass`, so its value is not displayed or stored in the notebook.

To run locally, activate your Python environment before opening Jupyter:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the local dependencies if needed:

```bash
python3 -m pip install -r requirements.txt
```

## Instructions

1. Open `start/01-first-bedrock-request.ipynb` in Google Colab or locally in Jupyter.
2. Read each markdown cell for context.
3. Find the `# TODO` comments and implement the required code.
4. Run each cell in order, confirm the offline acceptance check passes, and then send one live request.
5. Verify the notebook prints a non-empty answer and `MODEL_RESPONSE_OK model=openai.gpt-oss-20b-1:0`.

**Run command (local Jupyter):**

```bash
jupyter notebook start/01-first-bedrock-request.ipynb
```

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/labs/01-first-bedrock-request/start/01-first-bedrock-request.ipynb)

## Credential Safety

Use only a short-term lab key. Enter it only when the notebook prompts for it. Do not place it in source code, notebook text, screenshots, chat, or committed output. Restart the Colab runtime or Jupyter kernel after the lab to clear the in-memory key.

In production, prefer an IAM role or temporary AWS credentials with a supported token-refresh or AWS SDK authentication flow instead of manually distributing API keys.

## Getting Stuck?

The `solution/` directory contains a fully working reference notebook. Try each TODO on your own first, then compare with the solution.

Common live-call failures come from an incorrect Region, an expired key, unavailable model access, or a malformed regional endpoint. Preserve the exact error while troubleshooting, but never share the key.

## References

- [Amazon Bedrock quickstart](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)
- [OpenAI gpt-oss-20b model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-20b.html)
