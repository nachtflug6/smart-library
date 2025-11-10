"""Core metadata extraction logic (lean)."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import re

from smart_library.llm.client import BaseLLMClient
from smart_library.prompts.system_prompts import deterministic_extraction_prompt
from smart_library.prompts.user_prompts import metadata_extraction_prompt
from smart_library.extract.author_utils import clean_author
from smart_library.utils.parsing import parse_structured_obj
from smart_library.extract.base import extract_with_llm, extract_bulk_with_llm

EXPECTED_FIELDS = {
    "title",
    "authors",
    "venue",
    "year",
    "doi",
    "abstract",
    "keywords",
    "arxiv_id",
    "url",
}


def _normalize_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize raw metadata dict into expected schema."""
    out: Dict[str, Any] = {}
    for k in EXPECTED_FIELDS:
        v = raw.get(k, None)
        if k == "authors":
            if v is None:
                out[k] = None
            elif isinstance(v, list):
                cleaned = [c for a in v if (c := clean_author(str(a)))]
                out[k] = cleaned or None
            elif isinstance(v, str):
                parts = [p.strip() for p in re.split(r"[;,]", v) if p.strip()]
                cleaned = [c for a in parts if (c := clean_author(a))]
                out[k] = cleaned or None
            else:
                out[k] = None
        elif k == "keywords":
            if v is None:
                out[k] = None
            elif isinstance(v, list):
                kw = [str(x).strip().lower() for x in v if str(x).strip()]
                out[k] = kw or None
            elif isinstance(v, str):
                parts = [p.strip().lower() for p in re.split(r"[;,]", v) if p.strip()]
                out[k] = parts or None
            else:
                out[k] = None
        elif k == "year":
            if isinstance(v, int) and 1500 <= v <= 2100:
                out[k] = v
            elif isinstance(v, str) and v.isdigit():
                y = int(v)
                out[k] = y if 1500 <= y <= 2100 else None
            else:
                out[k] = None
        else:
            out[k] = v if (v is None or isinstance(v, (str, int))) else None
    return out


def extract_metadata(
    texts: List[str],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    enforce_json: bool = True,
    debug: bool = False,
) -> Dict[str, Any]:
    """Extract metadata from text using LLM."""
    if not texts:
        return {"error": "no_texts"}
    
    combined = "\n\n".join(t for t in texts if t)
    data, reason = extract_with_llm(
        combined,
        client,
        deterministic_extraction_prompt(),
        metadata_extraction_prompt,
        model=model,
        temperature=temperature,
        enforce_json=enforce_json,
        debug=debug,
    )
    
    if not isinstance(data, dict):
        return {"error": "invalid_json", "why": reason}
    return _normalize_metadata(data)


def extract_metadata_for_document(
    document_id: str,
    page_texts: List[str],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    max_pages: Optional[int] = 2,
) -> Dict[str, Any]:
    sample = page_texts[: max_pages] if max_pages else page_texts
    result = extract_metadata(sample, client, model=model)
    result["document_id"] = document_id
    return result


def extract_metadata_bulk(
    doc_texts: Dict[str, List[str]],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    max_workers: int = 6,
    max_pages_per_doc: int | None = 1,
    enforce_json: bool = True,
) -> List[Dict[str, Any]]:
    # Prepare inputs
    batch_inputs = []
    for doc_id, pages in doc_texts.items():
        usable = pages[: max_pages_per_doc] if max_pages_per_doc else pages
        text = "\n\n".join(p for p in usable if p)
        if text:
            batch_inputs.append((text, doc_id))
    
    # Extract
    bulk_results = extract_bulk_with_llm(
        batch_inputs,
        client,
        deterministic_extraction_prompt(),
        metadata_extraction_prompt,
        model=model,
        temperature=temperature,
        max_workers=max_workers,
        enforce_json=enforce_json,
    )
    
    # Process results
    results: List[Dict[str, Any]] = []
    for doc_id, raw, _ in bulk_results:
        data, reason = parse_structured_obj(raw)
        if not isinstance(data, dict):
            results.append({"document_id": doc_id, "error": "invalid_json", "why": reason})
            continue
        norm = _normalize_metadata(data)
        norm["document_id"] = doc_id
        results.append(norm)
    return results


