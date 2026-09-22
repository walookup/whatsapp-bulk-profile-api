#!/usr/bin/env bash
set -euo pipefail
: "${WALOOKUP_API_KEY:?Set WALOOKUP_API_KEY}"
PRODUCT="${PRODUCT:-ws_profile_batch}"
COUNTRY="${COUNTRY:-US}"
FILE="${FILE:-numbers.txt}"

task=$(curl -fsS -X POST 'https://walookup.com/api/v1/bulk-tasks' \
  -H "X-API-Key: $WALOOKUP_API_KEY" \
  -F "product=$PRODUCT" -F "country=$COUNTRY" -F "file=@$FILE")
echo "$task"
id=$(printf '%s' "$task" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')

# 轮询间隔不得短于 30 秒，这是服务端的契约而不是建议。
while true; do
  sleep 30
  body=$(curl -fsS "https://walookup.com/api/v1/bulk-tasks/$id" -H "X-API-Key: $WALOOKUP_API_KEY")
  echo "$body"
  printf '%s' "$body" | grep -q '"status":"processing"' || break
done
