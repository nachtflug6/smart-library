#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="data/pdf/pages"      # where your current files are
DST_DIR="data/pdf/pages_2"          # where we want the structured folders

mkdir -p "$DST_DIR"

for file in "$SRC_DIR"/*.txt; do
    fname=$(basename "$file" .txt)

    # Process ONLY files that include "_<number>"
    if [[ "$fname" == *_* ]]; then

        # Split into paper_id + page number
        paper_id="${fname%_*}"
        page="${fname##*_}"

        # Zero-pad page number
        printf -v page_padded "%02d" "$page"

        # Create target folder
        mkdir -p "$DST_DIR/$paper_id"

        # Move + rename file
        mv "$file" "$DST_DIR/$paper_id/p${page_padded}.txt"

        echo "[page] $fname → $paper_id/p${page_padded}.txt"

    else
        # Skip full-text/unstructured files
        echo "[skip] $fname (full text ignored)"
    fi
done