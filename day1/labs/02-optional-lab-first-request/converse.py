import boto3

REGION = "us-east-1"
client = boto3.client("bedrock-runtime", region_name=REGION)

response = client.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=[{
        "role": "user",
        "content": [{"text": "Please summarize the following customer support case for a retail return:\n\nCustomer: I received the wrong size for my shoes (Order #12345). I ordered a size 10 but received a size 8.\nAction required: Summarize the issue and suggest the next steps for the agent."}],
    }],
)
print(response["output"]["message"]["content"][0]["text"])
