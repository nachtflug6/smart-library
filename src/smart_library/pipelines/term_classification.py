"""End-to-end term context classification pipeline (I/O + orchestration)."""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

from smart_library.utils.io import read_jsonl
from smart_library.pipelines.base import get_llm_client, ensure_output_dir
from smart_library.extract.terms_classes import classify_term_contexts_bulk

IN_PATH = Path("data/jsonl/joins/terms_pages_context.jsonl")
OUT_PATH = Path("data/jsonl/joins/terms_pages_classified.jsonl")

def llm_term_context_classify(
    *,
    model: str = "gpt-5-mini",
    api_key: str | None = None,
    temperature: float = 0.2,
    batch_size: int = 20,
    include_unfound: bool = True,
    debug: bool = False,
    workers: int = 1,
    checkpoint_size: int | None = None,  # number of rows per high-level bucket (multiple batches)
) -> int:
    """
    Classify term contexts and write JSONL.
    Writes incrementally per high-level bucket (checkpoint).
    If checkpoint_size is None => single large run (current behavior but still streaming per bucket = one).
    In debug mode only one LLM batch (first batch_size rows).
    """
    if not IN_PATH.exists():
        print(f"Missing input: {IN_PATH}")
        return 0

    rows = read_jsonl(IN_PATH)
    if not rows:
        print(f"No rows in {IN_PATH}")
        return 0

    if include_unfound:
        work = rows
    else:
        work = [r for r in rows if r.get("context_status") == "found" and r.get("context")]

    if not work:
        print("No rows selected for classification.")
        ensure_output_dir(OUT_PATH)
        OUT_PATH.write_text("", encoding="utf-8")
        return 0

    if debug:
        work = work[:batch_size]
        workers = 1
        checkpoint_size = len(work)
        print(f"[DEBUG MODE] Limiting to first {len(work)} rows (one batch)")

    # Derive buckets
    if not checkpoint_size or checkpoint_size <= 0:
        checkpoint_size = len(work)  # single bucket

    buckets: List[List[Dict[str, Any]]] = []
    for i in range(0, len(work), checkpoint_size):
        buckets.append(work[i:i + checkpoint_size])

    client = get_llm_client(model=model, api_key=api_key)
    ensure_output_dir(OUT_PATH)

    written = 0
    bucket_count = len(buckets)
    mode = "w"
    with OUT_PATH.open(mode, encoding="utf-8") as f:
        for bi, bucket_rows in enumerate(buckets):
            print(f"[bucket {bi+1}/{bucket_count}] rows={len(bucket_rows)}")
            classified = classify_term_contexts_bulk(
                bucket_rows,
                client,
                model=model,
                temperature=temperature,
                batch_size=batch_size,
                debug=debug,
                workers=workers,
            )
            for row in classified:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
            f.flush()
            if debug:
                print(f"[DEBUG] Wrote bucket {bi+1} ({len(classified)} rows) cumulative={written}")

    print(f"✓ Wrote {written} classified rows -> {OUT_PATH}")
    return written