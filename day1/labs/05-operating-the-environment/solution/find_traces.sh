#!/bin/bash
# Usage: ./find_traces.sh <runtime-session-id>
SESSION_ID="$1"

echo "=== X-Ray trace summaries mentioning session $SESSION_ID ==="
aws xray get-trace-summaries \
  --start-time "$(date -u -v-1H +%s)" \
  --end-time "$(date -u +%s)" \
  --filter-expression "annotation.session_id = \"$SESSION_ID\""

echo
echo "=== CloudWatch Logs Insights query ==="
QUERY_ID=$(aws logs start-query \
  --log-group-name "/aws/bedrock/agentcore/team01" \
  --start-time "$(date -u -v-1H +%s)" \
  --end-time "$(date -u +%s)" \
  --query-string "fields @timestamp, @message | filter @message like /$SESSION_ID/ | sort @timestamp desc | limit 50" \
  --query "queryId" --output text)

sleep 3
aws logs get-query-results --query-id "$QUERY_ID"
