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

response = client.responses.create(
    model="us.openai.gpt-5.6-sol",
    input="Please summarize the following customer support case for a retail return:\n\nCustomer: I received the wrong size for my shoes (Order #12345). I ordered a size 10 but received a size 8.\nAction required: Summarize the issue and suggest the next steps for the agent.",
)
print(response.output_text)
