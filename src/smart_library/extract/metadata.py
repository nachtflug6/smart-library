import json
from pathlib import Path
from typing import Dict

from smart_library.llm.client import LLMClient  # your client
from smart_library.utils.io import read_text  # optional helper

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8")


def extract_metadata_for_document(
    document_id: str,
    pages_dir: Path,
    client: LLMClient,
    model: str = "gpt-5-mini",
) -> Dict:
    """
    Reads first 1–2 pages and extracts metadata via LLM.
    """
    pdir = pages_dir / document_id
    pages = sorted(pdir.glob("p*.txt"))

    if not pages:
        raise ValueError(f"No pages found for {document_id}")

    # Read first 2 pages or less if shorter
    sample_text = ""
    for p in pages[:2]:
        sample_text += p.read_text() + "\n\n"

    # Load prompt template
    prompt_template = Path("prompts/metadata_extraction.md").read_text()
    prompt = prompt_template + "\n\n---\nTEXT:\n" + sample_text

    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_output_tokens=400,
    )

    # Must be safe JSON
    try:
        data = json.loads(response)
    except Exception:
        return {"error": "invalid_json", "raw": response}

    data["document_id"] = document_id
    return data
