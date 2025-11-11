import json
import re
import random
from pathlib import Path

import pytest

from smart_library.utils.textmatch import verify_string_in_string

PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")
TERMS_PAGES_VERIFIED_PATH = Path("data/jsonl/joins/terms_pages_verified.jsonl")


@pytest.mark.smoke
def test_terms_context_smoke_20_random(capsys):
    if not TERMS_PAGES_VERIFIED_PATH.exists():
        pytest.skip("Run: python src/smart_library/cli/main.py terms-verify")
    if not PAGES_PATH.exists():
        pytest.skip("pages.jsonl missing")

    # Build (document_id,page)->path map
    pages_map = {}
    with PAGES_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            doc = obj.get("document_id")
            page = obj.get("page")
            path = obj.get("path")
            if isinstance(doc, str) and isinstance(page, int) and isinstance(path, str):
                pages_map[(doc, page)] = path

    # Load all verified occurrences
    all_rows = []
    with TERMS_PAGES_VERIFIED_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_rows.append(json.loads(line))

    if not all_rows:
        pytest.skip("terms_pages_verified.jsonl empty")

    # Random sample of up to 20 distinct rows
    sample_size = min(20, len(all_rows))
    random_rows = random.sample(all_rows, sample_size)

    def resolve_path(rel: str) -> Path | None:
        p = Path(rel)
        if p.exists():
            return p
        root = Path(__file__).resolve().parents[2]
        alt = root / rel
        return alt if alt.exists() else None

    def snippet(text: str, start: int, end: int, window: int = 180) -> str:
        s = max(0, start - window)
        e = min(len(text), end + window)
        before = text[s:start]
        match = text[start:end]
        after = text[end:e]
        collapse = lambda t: re.sub(r"\s+", " ", t).strip()
        return f"... {collapse(before)} [TERM:{match}] {collapse(after)} ..."

    found = 0
    print("\n===== Random term context smoke (sample {}) =====\n".format(sample_size))
    for i, r in enumerate(random_rows, 1):
        term = r.get("term")
        doc = r.get("document_id")
        page = r.get("page")
        key = (doc, page)
        print(f"{i}. '{term}' @ {doc}/p{page}")

        path = pages_map.get(key)
        if not path:
            print("   - no page mapping")
            continue
        txt_path = resolve_path(path)
        if not txt_path:
            print(f"   - file missing: {path}")
            continue
        try:
            text = txt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"   - read error: {e}")
            continue

        low_text = text.lower()
        low_term = (term or "").lower()
        idx = low_text.find(low_term)

        if idx >= 0:
            print("   ✓ exact")
            print("   ", snippet(text, idx, idx + len(term)))
            found += 1
            continue

        # fuzzy fallback
        if verify_string_in_string(term or "", text, fuzzy=True, tolerance=80):
            first_tok = low_term.split()[0] if low_term.split() else low_term
            approx = next((m.start() for m in re.finditer(re.escape(first_tok), low_text)), -1)
            if approx >= 0:
                start = approx
                end = min(len(text), start + max(len(term), 12))
                print("   ✓ fuzzy")
                print("   ", snippet(text, start, end))
            else:
                print("   ✓ fuzzy (span approx)")
            found += 1
        else:
            print("   ✗ not found")

    print(f"\nFound contexts for {found}/{sample_size} sampled terms\n")
    assert sample_size > 0