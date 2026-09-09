import json

import boto3

REGION = "us-east-1"
client = boto3.client("bedrock-runtime", region_name=REGION)

response = client.invoke_model(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn.",
        }],
        "max_tokens": 1024,
    }),
)
result = json.loads(response["body"].read())
print(result["content"][0]["text"])
