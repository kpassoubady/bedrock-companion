# Demo — Amazon Bedrock Guardrail Boundary

This is a live AWS follow-along demo for students.

## Instructions

1. Prefer running locally after `source ~/team-XX.env`. Never paste AWS credentials into notebook cells, outputs, screenshots, or committed files.
2. Open `demo-bedrock-guardrail-boundary.ipynb`. Use Colab only with an instructor-approved Secrets workflow.
3. Run all cells. The notebook creates a temporary Amazon Bedrock Guardrail, evaluates safe and unsafe inputs through the live `ApplyGuardrail` API, attaches the guardrail to a live Converse request, and deletes the temporary resource.

The notebook installs the course-pinned `boto3==1.43.62`. It uses `AWS_REGION` or `AWS_DEFAULT_REGION` and defaults to `us-east-1`. Do not interrupt the final code cell before its cleanup block runs. The cell retries deletion, verifies that the resource disappears, and prints the guardrail ID plus a manual AWS CLI cleanup command if deletion remains pending.

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/demos/demo-bedrock-guardrail-boundary/demo-bedrock-guardrail-boundary.ipynb)
