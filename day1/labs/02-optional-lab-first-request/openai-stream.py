import sys
from pathlib import Path

sys.path = [
    entry
    for entry in sys.path
    if Path(entry or ".").resolve() != Path(__file__).resolve().parent
]

from openai import OpenAI

REGION = "us-east-1"
client = OpenAI(
    base_url=f"https://bedrock-runtime.{REGION}.amazonaws.com/openai/v1"
)

stream = client.responses.create(
    model="us.openai.gpt-5.6-sol",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)

print()