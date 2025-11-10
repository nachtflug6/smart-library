import os
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

import pytest

from smart_library.llm.openai_client import OpenAIClient
from smart_library.extract.terms import extract_terms_bulk
from smart_library.utils.io import read_jsonl, now_iso

pytestmark = [pytest.mark.smoke, pytest.mark.external, pytest.mark.openai]


@pytest.mark.timeout(180)
def test_term_extraction_pipeline_to_jsonl(capsys, tmp_path):
    """
    Smoke test: extract terms from one random document (max 10 pages) 
    and write to terms_raw.jsonl and terms_pages_raw.jsonl.
    Validates the full pipeline output format.
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

    # Pick one random document with 3-10 pages
    candidates = [doc_id for doc_id, pgs in doc_pages.items() if 3 <= len(pgs) <= 10]
    if not candidates:
        pytest.skip("No documents with 3-10 pages found.")
    
    chosen_doc = random.choice(candidates)
    chosen_pages = doc_pages[chosen_doc]
    
    print(f"\n{'='*80}")
    print(f"Testing pipeline export for document: {chosen_doc}")
    print(f"Total pages: {len(chosen_pages)}")
    print(f"{'='*80}\n")

    client = OpenAIClient(
        api_key=api_key,
        default_model="gpt-5-mini",
        default_rpm=500,
        default_tpm=200_000,
    )

    # Extract terms
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

    # Aggregate unique terms and term-page associations
    unique_terms: set = set()
    term_pages: List[Dict] = []
    
    ts = now_iso()
    source = "llm:gpt-5-mini"
    
    print("Per-page extraction results:")
    for r in results:
        doc_id = r["document_id"]
        page = r["page"]
        terms = r.get("terms", [])
        
        print(f"  Page {page}: {len(terms)} terms")
        
        for term in terms:
            unique_terms.add(term)
            term_pages.append({
                "term": term,
                "document_id": doc_id,
                "page": page,
                "timestamp": ts,
                "source": source,
            })
    
    print(f"\nAggregated statistics:")
    print(f"  • Unique terms: {len(unique_terms)}")
    print(f"  • Term-page associations: {len(term_pages)}")
    
    # Write terms_raw.jsonl to tmp directory
    terms_raw_path = tmp_path / "terms_raw.jsonl"
    with terms_raw_path.open("w", encoding="utf-8") as f:
        for term in sorted(unique_terms):
            row = {
                "term": term,
                "timestamp": ts,
                "source": source,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    print(f"\n✓ Wrote {len(unique_terms)} unique terms to {terms_raw_path}")
    
    # Write terms_pages_raw.jsonl to tmp directory
    terms_pages_path = tmp_path / "terms_pages_raw.jsonl"
    with terms_pages_path.open("w", encoding="utf-8") as f:
        for row in term_pages:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    print(f"✓ Wrote {len(term_pages)} term-page associations to {terms_pages_path}")
    
    # Validate terms_raw.jsonl
    print(f"\n{'='*80}")
    print("VALIDATING terms_raw.jsonl")
    print(f"{'='*80}\n")
    
    terms_raw_data = read_jsonl(terms_raw_path)
    assert len(terms_raw_data) == len(unique_terms), \
        f"Expected {len(unique_terms)} rows in terms_raw.jsonl, got {len(terms_raw_data)}"
    
    print(f"✓ File contains {len(terms_raw_data)} rows")
    print(f"\nFirst 5 terms:")
    for i, row in enumerate(terms_raw_data[:5], 1):
        print(f"  {i}. {row['term']} (source: {row['source']}, timestamp: {row['timestamp']})")
    
    # Validate all rows have required fields
    for row in terms_raw_data:
        assert "term" in row, "Missing 'term' field"
        assert "timestamp" in row, "Missing 'timestamp' field"
        assert "source" in row, "Missing 'source' field"
        assert isinstance(row["term"], str), "term should be string"
        assert len(row["term"]) > 0, "term should not be empty"
    
    print(f"\n✓ All rows have required fields (term, timestamp, source)")
    
    # Validate terms_pages_raw.jsonl
    print(f"\n{'='*80}")
    print("VALIDATING terms_pages_raw.jsonl")
    print(f"{'='*80}\n")
    
    terms_pages_data = read_jsonl(terms_pages_path)
    assert len(terms_pages_data) == len(term_pages), \
        f"Expected {len(term_pages)} rows in terms_pages_raw.jsonl, got {len(terms_pages_data)}"
    
    print(f"✓ File contains {len(terms_pages_data)} rows")
    print(f"\nFirst 10 term-page associations:")
    for i, row in enumerate(terms_pages_data[:10], 1):
        print(f"  {i}. '{row['term']}' on page {row['page']} of {row['document_id']}")
    
    # Validate all rows have required fields
    for row in terms_pages_data:
        assert "term" in row, "Missing 'term' field"
        assert "document_id" in row, "Missing 'document_id' field"
        assert "page" in row, "Missing 'page' field"
        assert "timestamp" in row, "Missing 'timestamp' field"
        assert "source" in row, "Missing 'source' field"
        assert isinstance(row["term"], str), "term should be string"
        assert isinstance(row["document_id"], str), "document_id should be string"
        assert isinstance(row["page"], int), "page should be int"
        assert row["page"] > 0, "page should be positive"
    
    print(f"\n✓ All rows have required fields (term, document_id, page, timestamp, source)")
    
    # Check term frequency distribution
    term_freq = defaultdict(int)
    for row in terms_pages_data:
        term_freq[row["term"]] += 1
    
    print(f"\n📊 Term frequency distribution:")
    freq_sorted = sorted(term_freq.items(), key=lambda x: (-x[1], x[0]))
    print(f"  • Most frequent term: '{freq_sorted[0][0]}' ({freq_sorted[0][1]} occurrences)")
    if len(freq_sorted) > 1:
        print(f"  • Least frequent term: '{freq_sorted[-1][0]}' ({freq_sorted[-1][1]} occurrences)")
    
    # Show terms appearing on multiple pages
    multi_page_terms = [(term, count) for term, count in freq_sorted if count > 1]
    if multi_page_terms:
        print(f"\n📄 Terms appearing on multiple pages ({len(multi_page_terms)} terms):")
        for term, count in multi_page_terms[:10]:
            pages = [row["page"] for row in terms_pages_data if row["term"] == term]
            print(f"  • '{term}': {count} pages {sorted(pages)}")
    
    print(f"\n{'='*80}")
    print(f"✅ Pipeline smoke test PASSED")
    print(f"   • Extracted {len(unique_terms)} unique terms")
    print(f"   • Created {len(term_pages)} term-page associations")
    print(f"   • Both JSONL files validated successfully")
    print(f"{'='*80}\n")