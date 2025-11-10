"""End-to-end metadata extraction pipeline."""
import json
from pathlib import Path

from smart_library.extract.metadata import extract_metadata
from smart_library.utils.io import read_jsonl, now_iso
from smart_library.pipelines.base import (
    get_llm_client,
    load_first_page_map,
    ensure_output_dir,
    DOCUMENTS_PATH,
    PAGES_PATH,
)

OUT_PATH = Path("data/jsonl/joins/documents_metadata_llm.jsonl")


def llm_metadata_extract(
    *,
    model: str = "gpt-5-mini",
    api_key: str | None = None,
    output: Path = OUT_PATH,
    temperature: float = 1.0,
):
    """Extract metadata for all documents (first page only) and write to output JSONL."""
    if not DOCUMENTS_PATH.exists():
        raise FileNotFoundError(f"Missing {DOCUMENTS_PATH}")
    if not PAGES_PATH.exists():
        raise FileNotFoundError(f"Missing {PAGES_PATH}")

    docs = read_jsonl(DOCUMENTS_PATH)
    first_pages = load_first_page_map()
    if not first_pages:
        print("No first pages found.")
        return

    client = get_llm_client(model=model, api_key=api_key)
    ensure_output_dir(output)

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
                "metadata": None if ("error" in result) else result,
            }
            if isinstance(result, dict) and "error" in result:
                row["error"] = result["error"]

            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            written += 1

    print(f"✓ Wrote {written} metadata rows to {output}")