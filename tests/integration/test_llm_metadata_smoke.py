import os
import json
import random
from pathlib import Path
from typing import Any, Dict, List

import pytest

from smart_library.llm.openai_client import OpenAIClient
from smart_library.extract.metadata import extract_metadata_bulk

pytestmark = [pytest.mark.smoke, pytest.mark.external, pytest.mark.openai]


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def _load_first_pages(pages_jsonl: Path) -> Dict[str, str]:
    data = _read_jsonl(pages_jsonl)
    first_pages: Dict[str, str] = {}
    for p in data:
        try:
            if p.get("page") != 1:
                continue
            doc_id = p.get("document_id")
            path = p.get("path")
            if not doc_id or not path or doc_id in first_pages:
                continue
            page_path = Path(path)
            if not page_path.exists():
                continue
            first_pages[doc_id] = page_path.read_text(encoding="utf-8")
        except Exception:
            continue
    return first_pages


@pytest.mark.timeout(120)
def test_bulk_first_page_metadata_smoke_gpt5_mini(capsys):
    """
    Smoke test: sample up to 10 random documents (first page only), extract metadata in bulk using gpt-5-mini.
    Skips if OPENAI_API_KEY is not set or pages.jsonl is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping external smoke test.")

    pages_jsonl = Path("data/jsonl/entities/pages.jsonl")
    if not pages_jsonl.exists():
        pytest.skip(f"{pages_jsonl} not found; run data onboarding first.")

    first_pages = _load_first_pages(pages_jsonl)
    if not first_pages:
        pytest.skip("No valid first pages found.")

    # Sample size configurable via env; default 10
    sample_size = int(os.getenv("SMARTLIB_SMOKE_SIZE", "10"))
    random.seed(int(os.getenv("SMARTLIB_SMOKE_SEED", "42")))

    chosen_ids = (
        list(first_pages.keys())
        if len(first_pages) <= sample_size
        else random.sample(list(first_pages.keys()), sample_size)
    )
    doc_pages: Dict[str, List[str]] = {doc_id: [first_pages[doc_id]] for doc_id in chosen_ids}

    print(f"Testing bulk extraction on {len(doc_pages)} documents (first page only) using gpt-5-mini...")

    client = OpenAIClient(api_key=api_key, default_model="gpt-5-mini", default_rpm=500, default_tpm=200_000)

    results = extract_metadata_bulk(
        doc_texts=doc_pages,
        client=client,
        model="gpt-5-mini",
        max_workers=min(5, len(doc_pages)),
        max_pages_per_doc=None,
        debug=False,
    )

    assert len(results) == len(doc_pages), "Did not receive a result per requested document."

    expected_fields = {"title", "authors", "venue", "year", "doi", "keywords"}

    valid_count = 0
    for r in results:
        doc_id = r.get("document_id", "?")
        err = r.get("error")
        if err:
            print(f"{doc_id}: ERROR={err}")
            continue
        has_all = expected_fields.issubset(r.keys())
        if has_all:
            valid_count += 1
            print(f"{doc_id}: ✓ VALID")
            print(f"  title: {r.get('title')}")
            print(f"  authors: {r.get('authors')}")
            print(f"  venue: {r.get('venue')}")
            print(f"  year: {r.get('year')}")
        else:
            missing = expected_fields - set(r.keys())
            print(f"{doc_id}: ✗ MISSING_FIELDS -> {missing}")

    # Smoke expectation: at least one document should be valid
    assert valid_count >= 1, "No valid metadata entries extracted in smoke test."