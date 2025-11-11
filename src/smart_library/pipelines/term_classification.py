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
) -> int:
    """
    Read terms_pages_context.jsonl, classify term+context with LLM in batches,
    and write terms_pages_classified.jsonl with same rows + 'tags' + 'context_class'.
    
    In debug mode, only process one batch for quick testing.
    """
    if not IN_PATH.exists():
        print(f"Missing input: {IN_PATH}")
        return 0

    rows = read_jsonl(IN_PATH)
    if not rows:
        print(f"No rows in {IN_PATH}")
        return 0

    # Select rows
    work: List[Dict[str, Any]]
    if include_unfound:
        work = rows
    else:
        work = [r for r in rows if r.get("context_status") == "found" and r.get("context")]

    if not work:
        print("No rows selected for classification.")
        ensure_output_dir(OUT_PATH)
        OUT_PATH.write_text("", encoding="utf-8")
        return 0

    # In debug mode, limit to one batch
    if debug:
        work = work[:batch_size]
        print(f"[DEBUG MODE] Processing only first batch ({len(work)} rows)")

    client = get_llm_client(model=model, api_key=api_key)

    # Open file once, write after each batch
    ensure_output_dir(OUT_PATH)
    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for i in range(0, len(work), batch_size):
            batch_rows = work[i : i + batch_size]
            classified_batch = classify_term_contexts_bulk(
                batch_rows,
                client,
                model=model,
                temperature=temperature,
                batch_size=batch_size,  # process as single batch
                debug=debug,
            )
            for row in classified_batch:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
            if debug:
                print(f"[DEBUG] Wrote batch {i//batch_size + 1} ({len(classified_batch)} rows)")

    print(f"✓ Wrote {written} classified rows -> {OUT_PATH}")
    return written