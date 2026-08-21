import argparse
from pathlib import Path

import boto3

parser = argparse.ArgumentParser()
parser.add_argument("image", type=Path)
args = parser.parse_args()

REGION = "us-east-1"

image_formats = {
    ".gif": "gif",
    ".jpeg": "jpeg",
    ".jpg": "jpeg",
    ".png": "png",
    ".webp": "webp",
}
image_format = image_formats.get(args.image.suffix.lower())
if image_format is None:
    raise SystemExit("Image must be GIF, JPEG, PNG, or WebP")

client = boto3.client("bedrock-runtime", region_name=REGION)

# Load image from file
with args.image.open("rb") as f:
    image_bytes = f.read()

response = client.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=[{
        "role": "user",
        "content": [
            {"image": {
                "format": image_format,
                "source": {"bytes": image_bytes}
            }},
            {"text": "What is in this image? Describe the product for a retail return case."}
        ]
    }]
)
print(response["output"]["message"]["content"][0]["text"])
