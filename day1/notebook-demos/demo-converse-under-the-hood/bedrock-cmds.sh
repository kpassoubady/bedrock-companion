# Shared settings for all examples
export AWS_REGION="us-east-1"
export MODEL_ID="amazon.nova-lite-v1:0"

# Confirm which student identity is making the requests
aws sts get-caller-identity \
  --region "$AWS_REGION"

# Discover text-generation foundation models in the Region
aws bedrock list-foundation-models \
  --by-output-modality TEXT \
  --query 'modelSummaries[].{Name:modelName,Id:modelId,Streaming:responseStreamingSupported}' \
  --output table \
  --region "$AWS_REGION"

# Inspect the capabilities of the model used by the examples
aws bedrock get-foundation-model \
  --model-identifier "$MODEL_ID" \
  --query 'modelDetails.{Name:modelName,Id:modelId,Input:inputModalities,Output:outputModalities,Streaming:responseStreamingSupported,Inference:inferenceTypesSupported}' \
  --output json \
  --region "$AWS_REGION"

# Send a basic prompt and display the answer plus token and latency metrics
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"Reply with OK."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query '{Answer:output.message.content[?text].text | [0],StopReason:stopReason,Usage:usage,Latency:metrics.latencyMs}' \
  --output json \
  --region "$AWS_REGION"

# Use a system prompt to control the model's role and response style
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --system '[{"text":"You are an AWS instructor. Explain concepts in plain language using no more than two sentences."}]' \
  --messages '[{"role":"user","content":[{"text":"What is Amazon Bedrock?"}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Summarize operational text into a concise incident update
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"Summarize this customer support case for a retail return: Order #12345. Customer ordered a size 10 shoe but received a size 8. Action required: summarize the issue and next steps."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Classify customer feedback into one of a fixed set of labels
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --system '[{"text":"Classify sentiment as POSITIVE, NEGATIVE, or NEUTRAL. Return only the label."}]' \
  --messages '[{"role":"user","content":[{"text":"I am very frustrated that my retail order ORD-1042 arrived with the wrong shoe size."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Extract structured data from unstructured text
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --system '[{"text":"Extract the requested fields. Return only valid compact JSON with keys orderId, product, and priority."}]' \
  --messages '[{"role":"user","content":[{"text":"Urgent: Please process a return for order ORD-1042 containing one pair of running shoes."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Translate text while preserving its meaning and tone
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"Translate into French: Your order has shipped and will arrive tomorrow."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Supply conversation history so the model can answer a follow-up question
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"My Salesforce case number is 00001042."}]},{"role":"assistant","content":[{"text":"I have your case number as 00001042."}]},{"role":"user","content":[{"text":"What case number did I give you?"}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query 'output.message.content[?text].text | [0]' \
  --output text \
  --region "$AWS_REGION"

# Ask the model to select a tool and produce structured tool input
# This command demonstrates tool selection only; an application must execute the tool.
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"Check the status of Salesforce case 00001042."}]}]' \
  --tool-config '{"tools":[{"toolSpec":{"name":"lookup_case","description":"Read the current status and priority of a synthetic Salesforce support case.","inputSchema":{"json":{"type":"object","properties":{"caseNumber":{"type":"string"}},"required":["caseNumber"]}}}}]}' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query '{StopReason:stopReason,Content:output.message.content}' \
  --output json \
  --region "$AWS_REGION"

# Report the input, output, and total tokens consumed by an invocation
aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --messages '[{"role":"user","content":[{"text":"Explain the difference between a foundation model and an agent in one sentence."}]}]' \
  --inference-config '{"maxTokens":512,"temperature":0}' \
  --query '{Answer:output.message.content[?text].text | [0],InputTokens:usage.inputTokens,OutputTokens:usage.outputTokens,TotalTokens:usage.totalTokens}' \
  --output json \
  --region "$AWS_REGION"
