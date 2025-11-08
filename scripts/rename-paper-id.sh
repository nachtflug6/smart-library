#!/usr/bin/env bash

set -e

JOIN_DIR="../data/jsonl/joins"

echo "Renaming paper_id → document_id in $JOIN_DIR"

for file in "$JOIN_DIR"/*.jsonl; do
    [ -e "$file" ] || continue

    tmp="${file}.tmp"

    echo "Processing $file"

    # Replace the key
    sed 's/"paper_id"/"document_id"/g' "$file" > "$tmp"

    # Atomically replace
    mv "$tmp" "$file"
done

echo "Done."
