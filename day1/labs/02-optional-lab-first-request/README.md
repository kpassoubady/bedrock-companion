# Optional Breakout Lab: First Request

These examples correspond to the "First Request" optional lab in the course outline and the four API tabs in the [Amazon Bedrock quickstart](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html). They test basic API connectivity and model response handling within a retail customer support context.

| API | File | Python client | Authentication |
| --- | --- | --- | --- |
| Invoke | `invoke.py` | Boto3 | AWS credentials or Amazon Bedrock API key |
| Converse | `converse.py` | Boto3 | AWS credentials or Amazon Bedrock API key |
| Chat Completions | `chat-completions.py` | OpenAI SDK | Amazon Bedrock API key |
| Responses | `responses.py` | OpenAI SDK | Amazon Bedrock API key |

Each script makes a live model request and can incur AWS charges.

## Install

Use Python 3.10 or later in a virtual environment:

```bash
cd day1/labs/02-optional-lab-first-request
python3 -m venv .venv
source .venv/bin/activate
```

If you are using fish shell:

```bash
python3 --version
source .venv/bin/activate.fish
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Your prompt should show `(.venv)`. To leave later: `deactivate`


All examples are fixed to `us-east-1`, where the student lab role has access. Clear any old OpenAI endpoint override from the current shell:

```bash
unset OPENAI_BASE_URL
```

## Authentication

### Converse and Invoke APIs

Boto3 uses the standard AWS credential provider chain. It can also use the same short-term Bedrock API key when it is stored in `AWS_BEARER_TOKEN_BEDROCK`:

```bash
read -rsp "Short-term Bedrock API key: " AWS_BEARER_TOKEN_BEDROCK && echo
export AWS_BEARER_TOKEN_BEDROCK
```

Do not put credentials or API keys in source code, screenshots, notebooks, shell history, or Git. Use IAM roles or temporary credentials for production applications.

### Responses and Chat Completions APIs

Generate a short-term Amazon Bedrock API key in `us-east-1`, then configure the OpenAI SDK:

```bash
read -rsp "Short-term Bedrock API key: " OPENAI_API_KEY && echo
export OPENAI_API_KEY
```

The hidden prompt keeps the API key out of the command and shell history. Each OpenAI example explicitly uses `https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1`; it does not use `OPENAI_BASE_URL`.

## Run the four examples

Run only the APIs whose authentication you configured:

```bash
python invoke.py
python converse.py
python chat-completions.py
python responses.py
```

The OpenAI-compatible examples use `us.openai.gpt-5.6-sol`. The Converse and Invoke examples use `us.anthropic.claude-haiku-4-5-20251001-v1:0`. Confirm that these models are available to your account and Region. If your lab grants access to different models, update the model IDs before running the examples.

The path setup in the OpenAI examples prevents the existing local `openai.py` file from shadowing the installed `openai` package.

## Additional examples

- `openai.py` is the original AWS Responses API quick-start sample using `openai.gpt-oss-20b` on `bedrock-mantle`.
- `openai-stream.py` prints Responses API text as it arrives using `openai.gpt-oss-120b` on `bedrock-mantle`.
- `openai-images.py` sends a GIF, JPEG, PNG, or WebP image through Converse. Run `python openai-images.py path/to/image.jpg`; it defaults to `us-east-1`.

## Troubleshooting

- `ModuleNotFoundError`: activate the virtual environment and reinstall `requirements.txt`.
- Authentication errors: renew the API key or temporary AWS credentials without printing them.
- Model or access errors: verify the model ID, model availability, Region, and IAM permissions.
- Region errors: these examples are fixed to `us-east-1`. A `bedrock-mantle` or `us-west-2` error indicates stale endpoint configuration or an older copy of an example.
