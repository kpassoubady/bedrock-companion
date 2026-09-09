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

response = client.chat.completions.create(
    model="us.openai.gpt-5.6-sol",
    messages=[{
        "role": "user",
        "content": "Write a one-sentence bedtime story about a unicorn.",
    }],
)
print(response.choices[0].message.content)
