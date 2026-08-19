# Demo — Converse Under the Hood

This is a live AWS follow-along demo for students.

## Instructions

1. Prefer running locally after `source ~/team-XX.env`. Never paste AWS credentials into notebook cells, outputs, screenshots, or committed files.
2. Open `demo-converse-under-the-hood.ipynb`. Use Colab only with an instructor-approved Secrets workflow.
3. Run all cells and inspect the real Bedrock responses, token usage, message history, and tool-use exchange.

The notebook installs the course-pinned `boto3==1.43.62`. It uses `AWS_REGION` or `AWS_DEFAULT_REGION` and defaults to `us-east-1`. Override `MODEL_ID` if the instructor provides a different Converse-compatible model.

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/demos/demo-converse-under-the-hood/demo-converse-under-the-hood.ipynb)
