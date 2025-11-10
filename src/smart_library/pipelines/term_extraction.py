"""End-to-end term extraction pipeline."""
import json
from pathlib import Path
from typing import Set, List, Dict, Any

from smart_library.extract.terms import extract_terms_bulk
from smart_library.utils.io import now_iso
from smart_library.pipelines.base import (
    get_llm_client,
    load_all_pages,
    ensure_output_dir,
    PAGES_PATH,
)

TERMS_RAW_PATH = Path("data/jsonl/joins/terms_raw.jsonl")
TERMS_PAGES_RAW_PATH = Path("data/jsonl/joins/terms_pages_raw.jsonl")


def llm_term_extract(
    *,
    model: str = "gpt-5-mini",
    api_key: str | None = None,
    temperature: float = 1.0,
    max_workers: int = 6,
):
    """
    Extract terms from all document pages and write to:
    - terms_raw.jsonl: unique terms with metadata
    - terms_pages_raw.jsonl: term occurrences per document+page
    """
    if not PAGES_PATH.exists():
        raise FileNotFoundError(f"Missing {PAGES_PATH}")

    print("Loading all pages...")
    doc_pages = load_all_pages()
    if not doc_pages:
        print("No pages found.")
        return
    
    total_pages = sum(len(pages) for pages in doc_pages.values())
    print(f"Loaded {len(doc_pages)} documents with {total_pages} pages total.")

    client = get_llm_client(model=model, api_key=api_key)

    print(f"Extracting terms using {model}...")
    results = extract_terms_bulk(
        doc_pages=doc_pages,
        client=client,
        model=model,
        temperature=temperature,
        max_workers=max_workers,
        enforce_json=True,
    )

    # Aggregate unique terms and term-page associations
    unique_terms: Set[str] = set()
    term_pages: List[Dict[str, Any]] = []
    
    ts = now_iso()
    source = f"llm:{model}"
    
    for r in results:
        doc_id = r["document_id"]
        page = r["page"]
        terms = r.get("terms", [])
        
        for term in terms:
            unique_terms.add(term)
            term_pages.append({
                "term": term,
                "document_id": doc_id,
                "page": page,
                "timestamp": ts,
                "source": source,
            })
    
    # Write terms_raw.jsonl
    ensure_output_dir(TERMS_RAW_PATH)
    with TERMS_RAW_PATH.open("w", encoding="utf-8") as f:
        for term in sorted(unique_terms):
            row = {
                "term": term,
                "timestamp": ts,
                "source": source,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    print(f"✓ Wrote {len(unique_terms)} unique terms to {TERMS_RAW_PATH}")
    
    # Write terms_pages_raw.jsonl
    ensure_output_dir(TERMS_PAGES_RAW_PATH)
    with TERMS_PAGES_RAW_PATH.open("w", encoding="utf-8") as f:
        for row in term_pages:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    print(f"✓ Wrote {len(term_pages)} term-page associations to {TERMS_PAGES_RAW_PATH}")