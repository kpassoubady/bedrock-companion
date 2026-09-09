# Optional Lab: Send Your First Amazon Bedrock Request

This optional breakout exercise introduces the basic connection to Amazon Bedrock using the OpenAI-compatible Python SDK. It validates that your environment can communicate with the assigned models.

## Scenario and Goal

You are setting up the foundational connection for a new agentic application. Before building complex orchestration or memory management, you must verify that your AWS credentials allow invocation of the assigned model in the target Region.

**Goal:** Send a basic chat completions request to Amazon Bedrock and handle empty responses gracefully, ensuring your API key is never exposed.

## Time Budget

| Activity | Minutes |
| :--- | ---: |
| Review environment and prerequisites | 3 |
| Implement the prompt validation and API call | 7 |
| Run acceptance checks and live validation | 5 |
| **Total** | **15** |

Work individually or in pairs.

## Prerequisites

- Python 3.10 or later
- Local Jupyter notebook or Google Colab access
- An instructor-approved AWS Region where `openai.gpt-oss-20b-1:0` is available
- A short-term Amazon Bedrock API key

To run locally, activate your Python environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

## Checkpoint 1: Implement the Logic

Open `start/01-first-bedrock-request.ipynb` in your environment. Find the `# TODO` comments and implement the missing code in the `ask_bedrock` function.

1. Reject a blank prompt.
2. Call the injected OpenAI client's `chat.completions.create` exactly once.
3. Strip any `<reasoning>` block from the output.
4. Raise a RuntimeError if the resulting text is empty.

**Developer Prompt:**

If you are using a coding assistant, you can use the following prompt to help solve the TODOs:

```text
Complete the ask_bedrock function in 01-first-bedrock-request.ipynb. 
It must reject a blank prompt, call the injected OpenAI client's chat.completions.create 
exactly once, strip any <reasoning> block from the output, and raise a RuntimeError 
if the resulting text is empty. Do not change the function signature.
```

## Checkpoint 2: Validate and Run

Run each cell in order. First, confirm the offline acceptance check passes. Then, run the live cell to test your credentials.

**Run command (local Jupyter):**
```bash
jupyter notebook start/01-first-bedrock-request.ipynb
```

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/labs/01-first-bedrock-request/start/01-first-bedrock-request.ipynb)

## Definition of Done

- The offline `test_ask_bedrock` assertions pass.
- A non-empty answer is printed from the live Bedrock service.
- The marker `MODEL_RESPONSE_OK model=openai.gpt-oss-20b-1:0` appears in your output.
- No credentials exist in the source code or notebook output.

## Share-Out

Review your implementation and discuss:
- Why is it important to filter `<reasoning>` blocks before displaying the response to an end-user?
- What AWS credential mechanism would you use in production instead of manually distributing API keys?

## Where to Get Your API Key

The notebook prompts for a **short-term Amazon Bedrock API key** — this is not the same as the long-term IAM access key in your team's credentials file.

1. Sign in to the AWS Console with your assigned lab credentials.
2. Go to **Amazon Bedrock → API keys → Short-term API keys** tab, then click **Generate short-term API keys** (see `short-term-api-keys.png`).
3. In the dialog that opens, click **Copy API Key** to copy the `bedrock-api-key-...` value (see `copy-short-term-api-keys.png`).
4. Paste that value into the notebook's "Short-term Amazon Bedrock API key" prompt.

The key expires after 12 hours (or when your console session ends), matching the "short-term" credential safety guidance below.

## Credential Safety

Use only a short-term lab key. Enter it only when the notebook prompts for it. Do not place it in source code, notebook text, screenshots, chat, or committed output. Restart the Colab runtime or Jupyter kernel after the lab to clear the in-memory key.

## Getting Stuck?

1. Ensure your AWS Region supports the specified model.
2. Check that your API key is not expired.
3. Verify the regional endpoint URL is properly formed.
4. Compare your approach with `solution/01-first-bedrock-request.ipynb` in the repository.
