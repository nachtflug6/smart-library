"""End-to-end metadata extraction pipeline."""
import json
import os
from pathlib import Path
from typing import Dict

from smart_library.extract.metadata import extract_metadata
from smart_library.llm.openai_client import OpenAIClient
from smart_library.utils.io import read_jsonl, now_iso

OUT_PATH = Path("data/jsonl/joins/documents_metadata_llm.jsonl")
DOCUMENTS = Path("data/jsonl/entities/documents.jsonl")
PAGES = Path("data/jsonl/entities/pages.jsonl")


def _first_page_map() -> Dict[str, str]:
    """Return {document_id: path_to_first_page_txt}."""
    if not PAGES.exists():
        return {}
    pages = read_jsonl(PAGES)
    first: Dict[str, str] = {}
    for p in pages:
        if p.get("page") != 1:
            continue
        doc_id = p.get("document_id")
        path = p.get("path")
        if doc_id and path and doc_id not in first:
            first[doc_id] = path
    return first


def llm_metadata_extract(
    *,
    model: str = "gpt-5-mini",
    api_key: str | None = None,
    output: Path = OUT_PATH,
    temperature: float = 1.0,
):
    """Extract metadata for all documents (first page only) and write to output JSONL."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")
    if not DOCUMENTS.exists():
        raise FileNotFoundError(f"Missing {DOCUMENTS}")
    if not PAGES.exists():
        raise FileNotFoundError(f"Missing {PAGES}")

    docs = read_jsonl(DOCUMENTS)
    first_pages = _first_page_map()
    if not first_pages:
        print("No first pages found.")
        return

    client = OpenAIClient(
        api_key=api_key,
        default_model=model,
        default_rpm=500,
        default_tpm=200_000,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    ts = now_iso()
    source = f"llm:{model}"

    written = 0
    with output.open("a", encoding="utf-8") as f:
        for d in docs:
            doc_id = d.get("document_id")
            if not doc_id:
                continue
            page_path = first_pages.get(doc_id)
            if not page_path:
                continue
            pfile = Path(page_path)
            if not pfile.exists():
                continue
            try:
                text = pfile.read_text(encoding="utf-8")
            except Exception:
                continue

            result = extract_metadata(
                [text],
                client,
                model=model,
                temperature=temperature,
                enforce_json=True,
                debug=False,
            )

            row = {
                "document_id": doc_id,
                "timestamp": ts,
                "source": source,
                "prompt_version": None,
                # result is normalized dict on success; on error contains {"error": ...}
                "metadata": None if ("error" in result) else result,
            }
            if isinstance(result, dict) and "error" in result:
                row["error"] = result["error"]
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            written += 1

    print(f"✓ Wrote {written} metadata rows to {output}")