#!/usr/bin/env bash
# Convert entities/documents.jsonl → joins/documents_metadata_user.jsonl
# Usage:
#   ./scripts/move_metadata.sh [source]
# Example:
#   ./scripts/move_metadata.sh user
#   ./scripts/move_metadata.sh "llm:gpt-5-mini"

set -euo pipefail

IN="data/jsonl/entities/documents.jsonl"
OUT="data/jsonl/joins/documents_metadata_user.jsonl"
SOURCE="${1:-user}"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if [[ ! -f "$IN" ]]; then
  echo "Input not found: $IN" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required. Install with: apt update && apt install -y jq" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"

# Transform each JSONL row
jq -c --arg ts "$TS" --arg source "$SOURCE" '
  . as $in
  | {
      document_id: $in.document_id,
      timestamp: $ts,
      source: $source,
      prompt_version: null,
      metadata: {
        title: ($in.title // null),
        authors: null,
        venue: ($in.venue // null),
        year: ($in.year // null),
        doi: null,
        abstract: null,
        keywords: null,
        arxiv_id: null,
        url: null
      }
    }
' "$IN" > "$OUT"

echo "Wrote $OUT ($(wc -l < "$OUT") lines)"