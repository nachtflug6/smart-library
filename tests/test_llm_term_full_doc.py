import os
import random
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

import pytest

from smart_library.llm.openai_client import OpenAIClient
from smart_library.extract.terms import extract_terms_bulk
from smart_library.utils.io import read_jsonl

pytestmark = [pytest.mark.smoke, pytest.mark.external, pytest.mark.openai]


@pytest.mark.timeout(180)
def test_full_document_term_extraction_smoke(capsys):
    """
    Smoke test: extract terms from all pages of one random document (max 10 pages).
    Shows per-page extraction and final aggregated results.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping external smoke test.")

    pages_jsonl = Path("data/jsonl/entities/pages.jsonl")
    if not pages_jsonl.exists():
        pytest.skip(f"{pages_jsonl} not found; run data onboarding first.")

    pages = read_jsonl(pages_jsonl)
    
    # Group by document
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

    # Pick one random document with 3-10 pages (no fixed seed for true randomness)
    candidates = [doc_id for doc_id, pgs in doc_pages.items() if 3 <= len(pgs) <= 10]
    if not candidates:
        pytest.skip("No documents with 3-10 pages found.")
    
    chosen_doc = random.choice(candidates)
    chosen_pages = doc_pages[chosen_doc]
    
    print(f"\n{'='*80}")
    print(f"Testing full document term extraction: {chosen_doc}")
    print(f"Total pages: {len(chosen_pages)}")
    print(f"{'='*80}\n")

    client = OpenAIClient(
        api_key=api_key,
        default_model="gpt-5-mini",
        default_rpm=500,
        default_tpm=200_000,
    )

    results = extract_terms_bulk(
        doc_pages={chosen_doc: chosen_pages},
        client=client,
        model="gpt-5-mini",
        max_workers=6,
        enforce_json=True,
        debug=False,
    )

    assert len(results) == len(chosen_pages), \
        f"Expected {len(chosen_pages)} results, got {len(results)}."

    # Print per-page results
    print("\n" + "="*80)
    print("PER-PAGE EXTRACTION RESULTS")
    print("="*80 + "\n")
    
    page_term_map: Dict[int, List[str]] = {}
    all_terms: Dict[str, List[int]] = defaultdict(list)  # term -> [page_nums]
    
    for r in results:
        doc_id = r.get("document_id", "?")
        page = r.get("page", "?")
        terms = r.get("terms", [])
        err = r.get("error")
        
        page_term_map[page] = terms
        
        print(f"Page {page}:")
        if err:
            print(f"  ❌ ERROR: {err}")
        else:
            print(f"  ✓ Extracted {len(terms)} terms")
            if terms:
                # Show first 10 terms
                preview = terms[:10]
                print(f"  Terms: {', '.join(preview)}")
                if len(terms) > 10:
                    print(f"  ... and {len(terms) - 10} more")
            
            # Track which pages each term appears on
            for term in terms:
                all_terms[term].append(page)
        print()
    
    # Print aggregated results
    print("="*80)
    print("AGGREGATED RESULTS")
    print("="*80 + "\n")
    
    total_unique_terms = len(all_terms)
    total_term_page_pairs = sum(len(r.get("terms", [])) for r in results)
    
    print(f"📊 Statistics:")
    print(f"  • Total unique terms: {total_unique_terms}")
    print(f"  • Total term-page associations: {total_term_page_pairs}")
    print(f"  • Average terms per page: {total_term_page_pairs / len(results):.1f}")
    
    # Show top terms by frequency (appearing on most pages)
    term_freq = [(term, len(pages)) for term, pages in all_terms.items()]
    term_freq.sort(key=lambda x: (-x[1], x[0]))  # Sort by frequency desc, then alphabetically
    
    print(f"\n📈 Top 20 terms by page frequency:")
    for i, (term, freq) in enumerate(term_freq[:20], 1):
        pages_str = ", ".join(map(str, sorted(all_terms[term])))
        print(f"  {i:2d}. '{term}' - {freq} page(s) [{pages_str}]")
    
    # Show per-page tracking
    print(f"\n📄 Per-page term tracking:")
    for page in sorted(page_term_map.keys()):
        term_count = len(page_term_map[page])
        print(f"  Page {page:2d}: {term_count} terms")
    
    # All unique terms alphabetically
    print(f"\n📚 All unique terms (alphabetically):")
    sorted_terms = sorted(all_terms.keys())
    for i in range(0, len(sorted_terms), 5):
        chunk = sorted_terms[i:i+5]
        print(f"  {', '.join(chunk)}")
    
    print("\n" + "="*80 + "\n")
    
    # Assertions
    assert total_unique_terms > 0, "No terms extracted from any page."
    
    # Check that at least some pages have terms
    pages_with_terms = sum(1 for terms in page_term_map.values() if terms)
    assert pages_with_terms > 0, "No pages had any terms extracted."
    
    print(f"✅ Test passed: {pages_with_terms}/{len(results)} pages had terms extracted.")