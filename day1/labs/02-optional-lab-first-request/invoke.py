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
            "content": "Please summarize the following customer support case for a retail return:\n\nCustomer: I received the wrong size for my shoes (Order #12345). I ordered a size 10 but received a size 8.\nAction required: Summarize the issue and suggest the next steps for the agent.",
        }],
        "max_tokens": 1024,
    }),
)
result = json.loads(response["body"].read())
print(result["content"][0]["text"])
