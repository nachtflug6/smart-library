"""Core term extraction logic."""

from __future__ import annotations
from typing import Dict, Any, List
import re

from smart_library.llm.client import BaseLLMClient
from smart_library.prompts.system_prompts import deterministic_extraction_prompt
from smart_library.prompts.user_prompts import term_extraction_prompt
from smart_library.utils.parsing import parse_structured_obj
from smart_library.extract.base import extract_with_llm, extract_bulk_with_llm


def _normalize_term(raw: str) -> str | None:
    """Normalize a single term: lowercase, strip, validate."""
    if not raw:
        return None
    term = raw.strip().lower()
    if len(term) < 2 or len(term) > 100:
        return None
    if term.isdigit():
        return None
    return term or None


def _parse_terms_response(data: Any, reason: str, debug: bool = False) -> List[str]:
    """Extract and normalize terms from LLM response."""
    terms_list = []
    
    # Handle direct array response
    if isinstance(data, list):
        terms_list = data
    # Handle object with "terms" key
    elif isinstance(data, dict):
        if "terms" in data:
            terms_list = data["terms"]
        elif data:
            # Fallback: treat keys as terms
            terms_list = list(data.keys())
    
    if not isinstance(terms_list, list):
        if debug:
            print(f"[DEBUG] Invalid format: {reason}, data type={type(data)}, data={data}")
        return []
    
    # Normalize and deduplicate
    normalized = set()
    for t in terms_list:
        nt = _normalize_term(str(t))
        if nt:
            normalized.add(nt)
    
    if debug and normalized:
        print(f"[DEBUG] Normalized {len(normalized)} terms from {len(terms_list)} raw terms")
    
    return sorted(normalized)


def extract_terms_from_page(
    text: str,
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    enforce_json: bool = True,
    debug: bool = False,
) -> List[str]:
    """Extract technical terms from a single page of text."""
    data, reason = extract_with_llm(
        text,
        client,
        deterministic_extraction_prompt(),
        term_extraction_prompt,
        model=model,
        temperature=temperature,
        enforce_json=enforce_json,
        debug=debug,
    )
    
    if debug:
        if data is None:
            print(f"[DEBUG] Parsing failed: {reason}")
        else:
            print(f"[DEBUG] Parsed data type: {type(data)}, reason: {reason}")
    
    return _parse_terms_response(data, reason, debug)


def extract_terms_bulk(
    doc_pages: Dict[str, List[tuple[int, str]]],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    max_workers: int = 6,
    enforce_json: bool = True,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """
    Extract terms from multiple documents in parallel.
    
    Args:
        doc_pages: {document_id: [(page_num, page_text), ...]}
        
    Returns:
        List of dicts: [{"document_id": str, "page": int, "terms": [str]}]
    """
    # Prepare inputs
    batch_inputs = []
    for doc_id, pages in doc_pages.items():
        for page_num, page_text in pages:
            if page_text and page_text.strip():
                batch_inputs.append((page_text, (doc_id, page_num)))
    
    # Extract
    bulk_results = extract_bulk_with_llm(
        batch_inputs,
        client,
        deterministic_extraction_prompt(),
        term_extraction_prompt,
        model=model,
        temperature=temperature,
        max_workers=max_workers,
        enforce_json=enforce_json,
    )
    
    # Process results
    results: List[Dict[str, Any]] = []
    for (doc_id, page_num), raw, _ in bulk_results:
        if debug:
            print(f"\n[DEBUG] {doc_id} p{page_num} raw response (first 300 chars):\n{raw[:300]}")
        
        data, reason = parse_structured_obj(raw)
        
        if debug:
            print(f"[DEBUG] {doc_id} p{page_num} parsed: type={type(data)}, reason={reason}")
        
        terms = _parse_terms_response(data, reason, debug=debug)
        
        results.append({
            "document_id": doc_id,
            "page": page_num,
            "terms": terms,
        })
    
    return results