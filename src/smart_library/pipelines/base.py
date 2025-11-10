"""Shared pipeline utilities."""
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from smart_library.llm.openai_client import OpenAIClient
from smart_library.llm.client import BaseLLMClient
from smart_library.utils.io import read_jsonl

PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")
DOCUMENTS_PATH = Path("data/jsonl/entities/documents.jsonl")


def get_llm_client(
    model: str = "gpt-5-mini",
    api_key: str | None = None,
    default_rpm: int = 500,
    default_tpm: int = 200_000,
) -> BaseLLMClient:
    """Initialize OpenAI client with API key validation."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")
    
    return OpenAIClient(
        api_key=api_key,
        default_model=model,
        default_rpm=default_rpm,
        default_tpm=default_tpm,
    )


def load_first_page_map() -> Dict[str, str]:
    """Return {document_id: path_to_first_page_txt}."""
    if not PAGES_PATH.exists():
        return {}
    
    pages = read_jsonl(PAGES_PATH)
    first: Dict[str, str] = {}
    
    for p in pages:
        if p.get("page") != 1:
            continue
        doc_id = p.get("document_id")
        path = p.get("path")
        if doc_id and path and doc_id not in first:
            first[doc_id] = path
    
    return first


def load_all_pages() -> Dict[str, List[Tuple[int, str]]]:
    """Load all pages grouped by document_id with page numbers."""
    if not PAGES_PATH.exists():
        return {}
    
    pages = read_jsonl(PAGES_PATH)
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
    
    # Sort pages by page number
    for doc_id in doc_pages:
        doc_pages[doc_id].sort(key=lambda x: x[0])
    
    return dict(doc_pages)


def ensure_output_dir(path: Path) -> None:
    """Ensure output directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)