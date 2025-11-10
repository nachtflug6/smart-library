import os
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from smart_library.llm.openai_client import OpenAIClient
from smart_library.extract.terms import extract_terms_bulk
from smart_library.utils.io import read_jsonl

pytestmark = [pytest.mark.smoke, pytest.mark.external, pytest.mark.openai]


@pytest.mark.timeout(120)
def test_bulk_term_extraction_smoke_gpt5_mini(capsys):
    """
    Smoke test: extract terms from 5 random pages across different documents using gpt-5-mini.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping external smoke test.")

    pages_jsonl = Path("data/jsonl/entities/pages.jsonl")
    if not pages_jsonl.exists():
        pytest.skip(f"{pages_jsonl} not found; run data onboarding first.")

    pages = read_jsonl(pages_jsonl)
    
    # Group by document
    from collections import defaultdict
    doc_pages: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    for p in pages:
        doc_id = p.get("document_id")
        page_num = p.get("page")
        path = p.get("path")
        if not (doc_id and page_num and path):
            continue
        page_file = Path(path)
        if not page_file.exists():
            continue
        try:
            text = page_file.read_text(encoding="utf-8")
            doc_pages[doc_id].append((page_num, text))
        except Exception:
            continue
    
    if not doc_pages:
        pytest.skip("No valid pages found.")

    # Flatten all pages into a list of (doc_id, page_num, text) tuples
    all_pages: List[Tuple[str, int, str]] = []
    for doc_id, pages_list in doc_pages.items():
        for page_num, text in pages_list:
            all_pages.append((doc_id, page_num, text))
    
    if len(all_pages) < 5:
        pytest.skip(f"Not enough pages found. Need 5, got {len(all_pages)}.")
    
    # Select 5 random pages (different documents each time test runs)
    random.shuffle(all_pages)
    selected_pages = all_pages[:5]
    
    # Reorganize into doc_pages format for extract_terms_bulk
    test_doc_pages: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    for doc_id, page_num, text in selected_pages:
        test_doc_pages[doc_id].append((page_num, text))
    
    print(f"\nTesting term extraction on 5 random pages from {len(test_doc_pages)} documents using gpt-5-mini...")
    for doc_id, pages_list in test_doc_pages.items():
        page_nums = [p[0] for p in pages_list]
        print(f"  {doc_id}: pages {page_nums}")
    print()

    client = OpenAIClient(api_key=api_key, default_model="gpt-5-mini", default_rpm=500, default_tpm=200_000)

    results = extract_terms_bulk(
        doc_pages=test_doc_pages,
        client=client,
        model="gpt-5-mini",
        max_workers=5,
        enforce_json=True,
        debug=True,  # Enable debug output
    )

    assert len(results) == 5, f"Expected 5 results, got {len(results)}."

    # Print summary
    print("\n=== SUMMARY ===")
    for r in results:
        doc_id = r.get("document_id", "?")
        page = r.get("page", "?")
        terms = r.get("terms", [])
        err = r.get("error")
        
        print(f"\n{doc_id} p{page}:")
        if err:
            print(f"  ERROR={err}")
            if "raw_response" in r:
                print(f"  RAW (first 200): {r['raw_response']}")
            if "parsed_data" in r:
                print(f"  PARSED: {r['parsed_data']}")
        else:
            print(f"  {len(terms)} terms: {terms}")
    
    # Check if we got at least some terms across all pages
    total_terms = sum(len(r.get("terms", [])) for r in results)
    print(f"\nTotal terms extracted: {total_terms}")
    
    # Relaxed assertion: allow 0 terms but warn
    if total_terms == 0:
        pytest.fail("All 5 pages returned 0 terms. Prompt likely failing. Check debug output above.")