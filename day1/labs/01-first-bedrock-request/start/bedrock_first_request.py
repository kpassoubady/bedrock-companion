"""Send a first inference request through Amazon Bedrock's OpenAI-compatible API."""
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from openai import OpenAI

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH, override=True)

DEFAULT_MODEL_ID = "openai.gpt-oss-20b-1:0"
DEFAULT_PROMPT = "Explain three features of Amazon Bedrock for building generative AI applications."


def require_configuration():
    missing = [
        name
        for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL")
        if not os.environ.get(name)
    ]
    if missing:
        raise SystemExit(f"CONFIG_MISSING: set {', '.join(missing)} in .env")

    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    parsed_url = urlsplit(base_url)
    valid_hostname = re.fullmatch(
        r"bedrock-runtime\.[a-z0-9-]+\.amazonaws\.com(?:\.cn)?",
        parsed_url.hostname or "",
    )
    if (
        parsed_url.scheme != "https"
        or not valid_hostname
        or parsed_url.username
        or parsed_url.password
        or parsed_url.port
        or parsed_url.path != "/openai/v1"
        or parsed_url.query
        or parsed_url.fragment
    ):
        raise SystemExit(
            "CONFIG_INVALID: OPENAI_BASE_URL must use the regional Bedrock Runtime /openai/v1 endpoint"
        )


def ask_bedrock(client, prompt, model_id=DEFAULT_MODEL_ID):
    raise NotImplementedError(
        "TODO 1: validate the prompt, call client.chat.completions.create, and return non-empty message content"
    )


def main():
    require_configuration()
    answer = ask_bedrock(OpenAI(), DEFAULT_PROMPT)
    print(answer)
    print(f"\nMODEL_RESPONSE_OK model={DEFAULT_MODEL_ID}")


if __name__ == "__main__":
    main()
