"""Core metadata extraction logic (lean)."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import re

from smart_library.llm.client import LLMClient
from smart_library.extract.author_utils import clean_author
from smart_library.extract.base import extract_with_llm

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
                import re as _re
                parts = [p.strip() for p in _re.split(r"[;,]", v) if p.strip()]
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
                import re as _re
                parts = [p.strip().lower() for p in _re.split(r"[;,]", v) if p.strip()]
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


def deterministic_extraction_prompt() -> str:
    return (
        "You are a deterministic metadata extractor.\n"
        "- Do not hallucinate.\n"
        "- Use null for uncertain or missing fields.\n"
        "- When JSON is requested, return only valid JSON with no extra text.\n"
    )


def metadata_extraction_prompt(text: str, expected_format: str | None = None) -> str:
    fmt = expected_format or """
{
  "title": string | null,
  "authors": string[] | null,
  "venue": string | null,
  "year": integer | null,
  "doi": string | null,
  "abstract": string | null,
  "keywords": string[] | null,
  "arxiv_id": string | null,
  "url": string | null
}
""".strip()
    return f"""Extract bibliographic metadata from the paper TEXT.

Return STRICT JSON matching exactly this shape (no extra keys, no markdown):
{fmt}

Author formatting rules:
- Output each author as: Last, First Middle (academic format).
- If source is "First Middle Last", convert to "Last, First Middle".
- Preserve multi-word surnames and particles (e.g., "De Brouwer" -> "De Brouwer, Edward").
- Keep initials with periods (e.g., "J. B. Oliva" -> "Oliva, J. B.").
- Remove emails, ORCIDs, degrees, and markers (*, †, ‡, digits, indices).
- Collapse spaces; drop empty results; preserve original author order.

Other rules:
- Use null for missing or uncertain fields.
- year: integer (e.g., 2019).
- keywords: short lowercase phrases.
- Output ONLY the JSON object.

TEXT:
{text}
"""


class MetadataExtractor:
    """Extracts bibliographic metadata from document text using LLM."""

    def __init__(
        self,
        client: LLMClient,
        *,
        model: str = "gpt-4o-mini",
        temperature: float = 1.0,
        enforce_json: bool = True,
        debug: bool = False,
    ):
        """
        Initialize metadata extractor.

        Args:
            client: LLM client instance
            model: Model to use for extraction
            temperature: Sampling temperature
            enforce_json: Whether to enforce JSON response format
            debug: Enable debug logging
        """
        self.client = client
        self.model = model
        self.temperature = temperature
        self.enforce_json = enforce_json
        self.debug = debug

    def extract(self, texts: List[str]) -> Dict[str, Any]:
        """
        Extract metadata from text using LLM (single API call).

        Args:
            texts: List of text strings (typically pages from a document)

        Returns:
            Dict with normalized metadata fields
        """
        if not texts:
            return {"error": "no_texts"}

        combined = "\n\n".join(t for t in texts if t)
        data, reason = extract_with_llm(
            combined,
            self.client,
            deterministic_extraction_prompt(),
            metadata_extraction_prompt,
            model=self.model,
            temperature=self.temperature,
            enforce_json=self.enforce_json,
            debug=self.debug,
        )

        if not isinstance(data, dict):
            return {"error": "invalid_json", "why": reason}
        return _normalize_metadata(data)

    def extract_bulk(
        self,
        doc_texts: Dict[str, List[str]],
        *,
        max_pages_per_doc: Optional[int] = 1,
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata for multiple documents sequentially (one call per doc).

        Args:
            doc_texts: Dict mapping document_id to list of page texts
            max_pages_per_doc: Max pages to use per document (None = use all)

        Returns:
            List of metadata dicts with 'document_id' field added
        """
        results: List[Dict[str, Any]] = []
        for doc_id, pages in doc_texts.items():
            sample = pages[:max_pages_per_doc] if max_pages_per_doc else pages
            out = self.extract(sample)
            out["document_id"] = doc_id
            results.append(out)
        return results