#!/usr/bin/env bash
set -euo pipefail
: "${WALOOKUP_API_KEY:?Set WALOOKUP_API_KEY}"
API_BASE_URL="${API_BASE_URL:-https://walookup.com}"
API_BASE_URL="${API_BASE_URL%/}"
FILE="${FILE:-examples/numbers.txt}"
headers=(-H "X-API-Key: $WALOOKUP_API_KEY")
if [[ -n "${IDEMPOTENCY_KEY:-}" ]]; then
  headers+=(-H "Idempotency-Key: $IDEMPOTENCY_KEY")
fi
task=$(curl -fsS --max-time 180 -X POST "$API_BASE_URL/api/v1/bulk-tasks" \
  "${headers[@]}" \
  -F 'service_type=ws_avatar_batch' \
  -F "country=${COUNTRY:-US}" \
  -F "file=@$FILE")
echo "$task"
id=$(printf '%s' "$task" | python3 -c 'import json,sys; p=json.load(sys.stdin); sys.exit(str(p)) if p.get("code")!=0 else None; print(p["data"]["id"])')

while true; do
  sleep 30
  body=$(curl -fsS --max-time 60 "$API_BASE_URL/api/v1/bulk-tasks/$id" -H "X-API-Key: $WALOOKUP_API_KEY")
  echo "$body"
  status=$(printf '%s' "$body" | python3 -c 'import json,sys; p=json.load(sys.stdin); sys.exit(str(p)) if p.get("code")!=0 else None; d=p["data"]; print("ready" if d["status"]=="success" and d.get("result_url") else d["status"])')
  if [[ "$status" == failed ]]; then
    echo 'Task failed; inspect reason/reason_detail above.' >&2
    exit 1
  fi
  [[ "$status" == ready ]] && break
done
