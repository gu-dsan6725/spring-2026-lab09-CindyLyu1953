#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:9090}"
OUT_FILE="carol_output.txt"

if ! curl -sf "$BASE_URL/ping" >/dev/null; then
  echo "Server not reachable at $BASE_URL. Start it first:" >&2
  echo "  uv run uvicorn agent_api:app --reload --host 127.0.0.1 --port 9090" >&2
  exit 1
fi

post_turn() {
  local query="$1"
  curl -s -X POST "$BASE_URL/invocation" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
      --arg user_id "carol" \
      --arg run_id "carol-session-1" \
      --arg query "$query" \
      '{user_id: $user_id, run_id: $run_id, query: $query}')" \
    | jq -r '.response // ""'
}

append_turn() {
  local query="$1"
  local response
  response="$(post_turn "$query")"
  if [[ -z "${response// }" ]]; then
    response="(No response captured; rerun this script.)"
  fi
  {
    echo "User: $query"
    echo "Agent: $response"
    echo ""
  } >> "$OUT_FILE"
}

: > "$OUT_FILE"
append_turn "Hi, I'm Carol. I'm a data scientist."
append_turn "What programming languages do I like?"
append_turn "Do you know what Alice prefers?"
