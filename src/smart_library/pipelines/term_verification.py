from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from smart_library.utils.textmatch import verify_string_in_string

TERMS_RAW_PATH = Path("data/jsonl/joins/terms_raw.jsonl")
TERMS_PAGES_RAW_PATH = Path("data/jsonl/joins/terms_pages_raw.jsonl")
TERMS_PAGES_VERIFIED_PATH = Path("data/jsonl/joins/terms_pages_verified.jsonl")
TERMS_VERIFIED_PATH = Path("data/jsonl/joins/terms_verified.jsonl")
PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")

def _read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def _write_jsonl(path: Path, rows: List[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
    return len(rows)

def _load_page_text(txt_path: Path) -> str:
    with txt_path.open("r", encoding="utf-8") as f:
        return f.read()

def verify_terms_pipeline(*, fuzzy: bool = True, tolerance: int = 80) -> Dict[str, int]:
    """
    Read *_raw.jsonl, verify occurrences against page text, and write *_verified.jsonl.
    - terms_raw.jsonl -> terms_verified.jsonl (one row per unique verified term, row mirrors input)
    - terms_pages_raw.jsonl -> terms_pages_verified.jsonl (one row per verified page occurrence, row mirrors input)
    Nothing writes back to *_raw.jsonl.
    """
    # Load inputs
    terms_raw_rows = _read_jsonl(TERMS_RAW_PATH)
    terms_pages_rows = _read_jsonl(TERMS_PAGES_RAW_PATH)
    pages_rows = _read_jsonl(PAGES_PATH)

    # Build lookups
    term_meta: Dict[str, dict] = {}
    for r in terms_raw_rows:
        t = r.get("term")
        if isinstance(t, str) and t not in term_meta:
            term_meta[t] = r

    page_path_by_key: Dict[str, str] = {}
    for r in pages_rows:
        doc = r.get("document_id")
        pg = r.get("page")
        pth = r.get("path")
        if doc and isinstance(pg, int) and pth:
            page_path_by_key[f"{doc}_{pg}"] = pth

    # Verify occurrences
    verified_pages: List[dict] = []
    verified_terms_seen: set[str] = set()

    for occ in terms_pages_rows:
        term = occ.get("term")
        doc = occ.get("document_id")
        pg = occ.get("page")
        if not (isinstance(term, str) and isinstance(doc, str) and isinstance(pg, int)):
            continue

        key = f"{doc}_{pg}"
        rel_path = page_path_by_key.get(key)
        if not rel_path:
            continue

        txt_path = Path(rel_path)
        if not txt_path.exists():
            # Try resolve relative to repo root (this file -> project root assumption)
            root = Path(__file__).resolve().parents[3]
            alt = root / rel_path
            if alt.exists():
                txt_path = alt
            else:
                continue

        try:
            text = _load_page_text(txt_path)
        except Exception:
            continue

        if verify_string_in_string(term, text, fuzzy=fuzzy, tolerance=tolerance):
            verified_pages.append(occ)
            if term in term_meta and term not in verified_terms_seen:
                verified_terms_seen.add(term)

    # Prepare outputs mirroring input rows
    verified_terms_rows: List[dict] = [term_meta[t] for t in sorted(verified_terms_seen)]

    # Write outputs (overwrite each run)
    _write_jsonl(TERMS_PAGES_VERIFIED_PATH, verified_pages)
    _write_jsonl(TERMS_VERIFIED_PATH, verified_terms_rows)

    # Log absolute paths and counts for clarity
    print(f"Wrote terms_pages_verified.jsonl -> {TERMS_PAGES_VERIFIED_PATH.resolve()} ({len(verified_pages)} rows)")
    print(f"Wrote terms_verified.jsonl      -> {TERMS_VERIFIED_PATH.resolve()} ({len(verified_terms_rows)} rows)")

    return {
        "terms_verified": len(verified_terms_rows),
        "pages_verified": len(verified_pages),
        "terms_raw": len(terms_raw_rows),
        "pages_raw": len(terms_pages_rows),
    }