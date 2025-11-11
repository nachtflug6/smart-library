from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from smart_library.utils.jsonl import read_jsonl, write_jsonl
from smart_library.utils.pages import build_pages_index, read_page_text
from smart_library.utils.textmatch import verify_string_in_string

TERMS_RAW_PATH = Path("data/jsonl/joins/terms_raw.jsonl")
TERMS_PAGES_RAW_PATH = Path("data/jsonl/joins/terms_pages_raw.jsonl")
TERMS_PAGES_VERIFIED_PATH = Path("data/jsonl/joins/terms_pages_verified.jsonl")
TERMS_VERIFIED_PATH = Path("data/jsonl/joins/terms_verified.jsonl")
PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")

def verify_terms_pipeline(*, fuzzy: bool = True, tolerance: int = 80, debug: bool = False) -> Dict[str, int]:
    """
    Read *_raw.jsonl, verify occurrences against page text, and write *_verified.jsonl.
    - terms_raw.jsonl -> terms_verified.jsonl (one row per unique verified term, row mirrors input)
    - terms_pages_raw.jsonl -> terms_pages_verified.jsonl (one row per verified page occurrence, row mirrors input)
    Nothing writes back to *_raw.jsonl.
    """
    # Load inputs via shared utils
    terms_raw_rows = read_jsonl(TERMS_RAW_PATH)
    terms_pages_rows = read_jsonl(TERMS_PAGES_RAW_PATH)
    pages_idx = build_pages_index(PAGES_PATH)

    # Build lookup for term metadata
    term_meta: Dict[str, dict] = {}
    for r in terms_raw_rows:
        t = r.get("term")
        if isinstance(t, str) and t not in term_meta:
            term_meta[t] = r

    # Stats
    dropped_no_mapping = 0
    dropped_missing_file = 0
    dropped_read_error = 0
    dropped_no_match = 0

    verified_pages: List[dict] = []
    verified_terms_seen: set[str] = set()

    for occ in terms_pages_rows:
        term = occ.get("term")
        doc = occ.get("document_id")
        pg = occ.get("page")
        if not (isinstance(term, str) and isinstance(doc, str) and isinstance(pg, int)):
            continue

        rel_path = pages_idx.get((doc, pg))
        if not rel_path:
            dropped_no_mapping += 1
            if debug:
                print(f"[verify] No mapping for {doc}_{pg}")
            continue

        text = read_page_text(rel_path)
        if text is None:
            dropped_missing_file += 1
            if debug:
                print(f"[verify] Missing/unreadable page file: {rel_path}")
            continue

        hit = verify_string_in_string(term, text, fuzzy=fuzzy, tolerance=tolerance)

        if hit:
            verified_pages.append(occ)
            if term in term_meta and term not in verified_terms_seen:
                verified_terms_seen.add(term)
        else:
            dropped_no_match += 1

    verified_terms_rows: List[dict] = [term_meta[t] for t in sorted(verified_terms_seen)]

    # Write outputs via shared utils
    write_jsonl(TERMS_PAGES_VERIFIED_PATH, verified_pages)
    write_jsonl(TERMS_VERIFIED_PATH, verified_terms_rows)

    print(f"Wrote terms_pages_verified.jsonl -> {TERMS_PAGES_VERIFIED_PATH.resolve()} ({len(verified_pages)} rows)")
    print(f"Wrote terms_verified.jsonl      -> {TERMS_VERIFIED_PATH.resolve()} ({len(verified_terms_rows)} rows)")
    if debug:
        print(f"[verify] Stats: no_mapping={dropped_no_mapping}, missing_file={dropped_missing_file}, "
              f"read_error={dropped_read_error}, no_match={dropped_no_match}")

    return {
        "terms_verified": len(verified_terms_rows),
        "pages_verified": len(verified_pages),
        "terms_raw": len(terms_raw_rows),
        "pages_raw": len(terms_pages_rows),
        "no_mapping": dropped_no_mapping,
        "missing_file": dropped_missing_file,
        "read_error": dropped_read_error,
        "no_match": dropped_no_match,
    }