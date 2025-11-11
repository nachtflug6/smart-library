from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from smart_library.utils.textmatch import verify_string_in_string  # fuzzy / strict
from smart_library.utils.textnorm import normalize_term, normalize_text_window
from smart_library.utils.jsonl import read_jsonl, write_jsonl
from smart_library.utils.pages import build_pages_index, read_page_text

TERMS_PAGES_VERIFIED_PATH = Path("data/jsonl/joins/terms_pages_verified.jsonl")
PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")
OUTPUT_PATH = Path("data/jsonl/joins/terms_pages_context.jsonl")

def _normalize(s: str) -> str:
    return normalize_text_window(s)

def _find_match_span(term: str, text: str, fuzzy: bool, tolerance: int) -> Optional[Tuple[int,int,int,str]]:
    # Return (start,end,score,method)
    lower_text = text.lower()
    lower_term = term.lower()
    idx = lower_text.find(lower_term)
    if idx != -1:
        return idx, idx + len(lower_term), 100, "exact"
    if fuzzy and verify_string_in_string(term, text, fuzzy=True, tolerance=tolerance):
        # crude fuzzy span: try anchoring on first token
        toks = lower_term.split()
        anchor = toks[0] if toks else lower_term
        positions = [m.start() for m in re.finditer(re.escape(anchor), lower_text)]
        best = None
        for pos in positions:
            window = lower_text[pos:pos+len(lower_term)+50]
            score = 100
            end_guess = pos + len(window)
            cand = (pos, min(end_guess, len(text)), score, "fuzzy")
            if not best:
                best = cand
        return best
    return None

def _extract_context(text: str, start: int, end: int, window_tokens: int) -> str:
    before = text[:start]
    match = text[start:end]
    after = text[end:]
    before_tokens = normalize_text_window(before).split()
    after_tokens = normalize_text_window(after).split()
    before_slice = before_tokens[-window_tokens:]
    after_slice = after_tokens[:window_tokens]
    match_norm = normalize_term(match)
    context = "…" + " ".join(before_slice) + f" [TERM:{match_norm}] " + " ".join(after_slice) + "…"
    return context.strip()

def enrich_term_page_context(
    window_tokens: int = 40,
    fuzzy: bool = True,
    tolerance: int = 80,
    limit_per_row: int = 1
) -> int:
    verified_rows = read_jsonl(TERMS_PAGES_VERIFIED_PATH)
    pages_idx = build_pages_index(PAGES_PATH)

    output: List[dict] = []
    for row in verified_rows:
        term = row.get("term")
        doc = row.get("document_id")
        page = row.get("page")
        if not (isinstance(term, str) and isinstance(doc, str) and isinstance(page, int)):
            continue

        rel_path = pages_idx.get((doc, page))
        if not rel_path:
            row["context"] = None
            row["context_method"] = None
            row["context_status"] = "missing_page_mapping"
            output.append(row)
            continue

        text = read_page_text(rel_path)
        if text is None:
            row["context"] = None
            row["context_method"] = None
            row["context_status"] = "missing_file"
            output.append(row)
            continue

        span = _find_match_span(term, text, fuzzy=fuzzy, tolerance=tolerance)
        if span:
            start, end, score, method = span
            row["context"] = _extract_context(text, start, end, window_tokens)
            row["context_method"] = method
            row["context_score"] = score
            row["context_status"] = "found"
            row["context_start"] = start
            row["context_end"] = end
            row["term_normalized"] = normalize_term(term)
        else:
            row["context"] = None
            row["context_method"] = None
            row["context_score"] = None
            row["context_status"] = "not_found"
            row["term_normalized"] = normalize_term(term)

        output.append(row)

    written = write_jsonl(OUTPUT_PATH, output)
    print(f"Wrote enriched context rows -> {OUTPUT_PATH.resolve()} ({written} rows)")
    return written