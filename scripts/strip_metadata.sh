#!/usr/bin/env bash
set -euo pipefail

IN="data/jsonl/entities/documents.jsonl"
TMP="${IN}.tmp"

if [[ ! -f "$IN" ]]; then
  echo "Missing $IN" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq required (apt update && apt install -y jq)" >&2
  exit 1
fi

jq -c '{document_id, pdf_path, page_count}' "$IN" > "$TMP"
mv "$TMP" "$IN"
echo "Stripped metadata fields from $IN"